from __future__ import annotations

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app import boi_canh, throttle
from app.accounts import (
    MIN_AGE,
    check_password,
    clean_name,
    create_user,
    email_looks_wrong,
    email_taken,
    find_by_email,
    message_for,
    normalise_email,
    parse_age,
)
from app.auth import clear_session, get_current_user, set_session
from app.dat_lai import dat_lai, doc_ve, tao_ve, than_thu
from app.mail import gui as gui_thu
from app.oauth import bat as oauth_bat
from app.oauth import dang_bat as oauth_dang_bat
from app.oauth import doc_userinfo, noi_tai_khoan
from app.oauth import khach as oauth_khach
from app.db import get_db
from app.config import PHIEN_BAN_DIEU_KHOAN, PHIEN_BAN_RIENG_TU, PILOT_16_PLUS
from app.models import Class, ClassMembership, Consent, User
from app.scenarios import all_scenarios
from app.schools import truong_dang_nhan, truong_theo_ma
from app.security import hash_password, needs_rehash, verify_password
from app.templating import templates

log = logging.getLogger("gals.auth")

router = APIRouter()

AVATARS = [
    {"id": "avatar-1", "emoji": "🦊", "label": "Cáo"},
    {"id": "avatar-2", "emoji": "🦉", "label": "Cú"},
    {"id": "avatar-3", "emoji": "🐢", "label": "Rùa"},
    {"id": "avatar-4", "emoji": "🦋", "label": "Bướm"},
    {"id": "avatar-5", "emoji": "🐬", "label": "Cá heo"},
    {"id": "avatar-6", "emoji": "🦌", "label": "Hươu"},
    {"id": "avatar-7", "emoji": "🐝", "label": "Ong"},
    {"id": "avatar-8", "emoji": "🦜", "label": "Vẹt"},
]

AVATAR_EMOJI = {a["id"]: a["emoji"] for a in AVATARS}
templates.env.globals["avatar_emoji"] = AVATAR_EMOJI


def _signed_in(request: Request, user: User, destination: str) -> RedirectResponse:
    response = RedirectResponse(destination, status_code=303)
    set_session(request, response, user.id, user)
    return response


def _home_for(user: User) -> str:
    return "/giao-vien" if user.is_teacher else "/trang-ca-nhan"


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "khong-ro"


def _ghi_dong_y(db: Session, user: User) -> None:
    """Lưu bằng chứng đã đồng ý, kèm phiên bản văn bản.

    PDPL đòi hỏi chứng minh được đã có đồng ý, mà một ô tích không để lại dấu
    vết thì không chứng minh được gì. Không lưu địa chỉ máy: bản thân nó cũng
    là dữ liệu cá nhân, và cặp phiên bản + thời điểm đã đủ.
    """
    db.add_all(
        [
            Consent(user_id=user.id, loai="rieng_tu", phien_ban=PHIEN_BAN_RIENG_TU),
            Consent(user_id=user.id, loai="dieu_khoan", phien_ban=PHIEN_BAN_DIEU_KHOAN),
        ]
    )
    db.commit()


def _join_class(db: Session, user: User, ma_lop: str) -> bool:
    """Vào lớp theo mã. Trả về False nếu mã không khớp lớp nào."""
    code = (ma_lop or "").strip().upper()
    if not code:
        return False
    klass = db.query(Class).filter(Class.class_code == code).first()
    if klass is None:
        return False
    already = (
        db.query(ClassMembership.id)
        .filter(
            ClassMembership.student_id == user.id,
            ClassMembership.class_id == klass.id,
        )
        .first()
    )
    if already is None:
        db.add(ClassMembership(student_id=user.id, class_id=klass.id))
        db.commit()
    return True


@router.get("/", response_class=HTMLResponse)
def landing(request: Request, user: User | None = Depends(get_current_user)):
    return templates.TemplateResponse(
        request,
        "auth/landing.html",
        {"user": None, "logged_in": user is not None, "scenarios": all_scenarios()},
    )


@router.get("/dang-nhap", response_class=HTMLResponse)
def login_form(request: Request, loi: str = ""):
    return templates.TemplateResponse(
        request,
        "auth/login.html",
        {"user": None, "loi": message_for(loi), "oauth": oauth_dang_bat()},
    )


@router.post("/dang-nhap")
def login_submit(
    request: Request,
    email: str = Form(""),
    mat_khau: str = Form(""),
    db: Session = Depends(get_db),
):
    address = normalise_email(email)
    # Đếm theo cả email lẫn địa chỉ máy: chặn theo email thôi thì một máy có thể
    # rải đều qua nhiều email, chặn theo máy thôi thì cả phòng máy trường học
    # dùng chung một địa chỉ sẽ khoá lẫn nhau.
    keys = [f"dn:email:{address}", f"dn:ip:{_client_ip(request)}"]
    if any(throttle.blocked(k) for k in keys):
        return RedirectResponse("/dang-nhap?loi=thu_lai_sau", status_code=303)

    user = find_by_email(db, address)
    stored = user.password_hash if user else None
    # verify_password vẫn băm một lần khi không có tài khoản, nên thời gian trả
    # lời không tiết lộ email nào đã đăng ký.
    if not verify_password(mat_khau, stored):
        for k in keys:
            throttle.record_failure(k)
        # Một câu duy nhất cho cả "chưa có email này" lẫn "sai mật khẩu".
        return RedirectResponse("/dang-nhap?loi=sai_thong_tin", status_code=303)

    for k in keys:
        throttle.clear(k)

    if needs_rehash(stored):
        # Lần đăng nhập là dịp duy nhất nâng tham số Argon2 mà không cần biết
        # mật khẩu gốc, vì chỉ lúc này mới có bản rõ trong tay.
        user.password_hash = hash_password(mat_khau)
    user.last_login_at = datetime.now()
    db.commit()

    return _signed_in(request, user, _home_for(user))


@router.get("/dang-ky", response_class=HTMLResponse)
def signup_form(request: Request, loi: str = "", ma_lop: str = ""):
    return templates.TemplateResponse(
        request,
        "auth/signup.html",
        {
            "user": None,
            "loi": message_for(loi),
            "ma_lop": ma_lop,
            "tuoi_toi_thieu": MIN_AGE,
            "pilot_16_plus": PILOT_16_PLUS,
            "oauth": oauth_dang_bat(),
        },
    )


@router.get("/dang-ky/can-ma-lop", response_class=HTMLResponse)
def need_class_code(request: Request):
    """Dưới 16 tuổi và không có mã lớp thì dừng ở đây.

    Không phải để loại các em ra, mà vì con đường đúng đi qua nhà trường: ở đó
    quan hệ với phụ huynh đã có sẵn và cơ sở pháp lý là của trường.
    """
    return templates.TemplateResponse(
        request,
        "auth/can_ma_lop.html",
        {"user": None, "tuoi_toi_thieu": MIN_AGE},
    )


@router.get("/dang-ky/chua-du-tuoi", response_class=HTMLResponse)
def pilot_age_limited(request: Request):
    """Đợt thử nghiệm 16+: dưới 16 thì mã lớp cũng không mở được cửa.

    Trang riêng chứ không dùng lại trang "cần mã lớp", vì hai câu trả lời khác
    hẳn nhau. Trang kia bảo *đi xin mã lớp đi*; trang này phải nói thật rằng lúc
    này chưa có đường nào, kể cả có mã lớp — bảo một em đi xin thứ không dùng
    được là để em chạy một vòng vô ích.
    """
    return templates.TemplateResponse(
        request,
        "auth/chua_du_tuoi.html",
        {"user": None, "tuoi_toi_thieu": MIN_AGE},
    )


@router.post("/dang-ky")
def signup_submit(
    request: Request,
    ten: str = Form(""),
    email: str = Form(""),
    mat_khau: str = Form(""),
    mat_khau_lai: str = Form(""),
    tuoi: str = Form(""),
    ma_lop: str = Form(""),
    dong_y: str = Form(""),
    db: Session = Depends(get_db),
):
    code = (ma_lop or "").strip().upper()

    def back(loi: str) -> RedirectResponse:
        target = f"/dang-ky?loi={loi}"
        if code:
            target += f"&ma_lop={code}"
        return RedirectResponse(target, status_code=303)

    name, problem = clean_name(ten)
    if problem:
        return back(problem)

    age = parse_age(tuoi)
    if age is None:
        return back("tuoi_hong")

    has_class = bool(code) and (
        db.query(Class.id).filter(Class.class_code == code).first() is not None
    )
    if age < MIN_AGE and (PILOT_16_PLUS or not has_class):
        # Tuổi tự khai không phải là xác minh — đây là chỉ dẫn đường đi, và cả
        # giao diện lẫn LEGAL.md đều nói đúng như vậy.
        #
        # Trong đợt thử nghiệm 16+, mã lớp không mở được cánh cửa này nữa: lối
        # cũ dựa vào việc nhà trường đã xin phép gia đình, mà đợt này không có
        # đường đồng ý nào của người giám hộ được dựng hay được thử.
        dich = "/dang-ky/chua-du-tuoi" if PILOT_16_PLUS else "/dang-ky/can-ma-lop"
        return RedirectResponse(dich, status_code=303)
    if code and not has_class:
        return back("ma_lop_sai")

    address = normalise_email(email)
    if email_looks_wrong(address):
        return back("email_hong")
    if email_taken(db, address):
        # Ở đây thì không giấu được: người dùng phải biết vì sao không tạo được
        # tài khoản. Việc chống dò email dồn hết sang trang đăng nhập.
        return back("email_trung")

    if (problem := check_password(mat_khau)) is not None:
        return back(problem)
    # Hỏi hai lần: gõ nhầm một chữ ở đây là khoá cửa ngay, và đường cứu hộ
    # (đặt lại mật khẩu) lại đi qua chính địa chỉ email vừa gõ ở trên.
    if mat_khau_lai != mat_khau:
        return back("mat_khau_lech")

    if not dong_y:
        return back("chua_dong_y")

    user = create_user(db, name=name, email=address, password=mat_khau)
    _ghi_dong_y(db, user)
    if code:
        _join_class(db, user, code)

    return _signed_in(request, user, "/chon-avatar")


@router.get("/chon-khong-gian", response_class=HTMLResponse)
def context_form(
    request: Request,
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user is None:
        return RedirectResponse("/dang-nhap", status_code=303)
    return templates.TemplateResponse(
        request,
        "auth/chon_khong_gian.html",
        {
            "user": user,
            "focus": True,
            "lua_chon": boi_canh.lua_chon(db, user),
            "dang_chon": boi_canh.doc(request, db, user),
        },
    )


@router.post("/chon-khong-gian")
def context_submit(
    request: Request,
    khoa: str = Form(""),
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user is None:
        return RedirectResponse("/dang-nhap", status_code=303)

    chon = next((bc for bc in boi_canh.lua_chon(db, user) if bc.khoa == khoa), None)
    if chon is None:
        # Khoá lạ, hoặc lớp không còn thuộc về mình. Hỏi lại chứ không đoán.
        return RedirectResponse("/chon-khong-gian", status_code=303)

    response = RedirectResponse(_home_for(user), status_code=303)
    boi_canh.ghi(request, response, chon)
    return response


@router.get("/quen-mat-khau", response_class=HTMLResponse)
def forgot_form(request: Request, loi: str = "", da_gui: str = ""):
    return templates.TemplateResponse(
        request,
        "auth/quen_mat_khau.html",
        {"user": None, "loi": message_for(loi), "da_gui": bool(da_gui)},
    )


@router.post("/quen-mat-khau")
def forgot_submit(
    request: Request,
    email: str = Form(""),
    db: Session = Depends(get_db),
):
    address = normalise_email(email)
    key = f"quen:ip:{_client_ip(request)}"
    if throttle.blocked(key):
        return RedirectResponse("/quen-mat-khau?loi=thu_lai_sau", status_code=303)
    throttle.record_failure(key)

    user = find_by_email(db, address)
    if user is not None:
        token = tao_ve(db, user)
        lien_ket = str(request.url_for("reset_form")) + f"?token={token}"
        tieu_de, than = than_thu(lien_ket)
        if not gui_thu(user.email, tieu_de, than):
            # Chưa cấu hình dịch vụ thư. Vé vẫn có thật, và
            # `python -m app.quan_tri dat-lai <email>` in lại được liên kết.
            log.warning("Không gửi được thư đặt lại mật khẩu cho user id=%s.", user.id)

    # Trả lời y hệt nhau dù địa chỉ có tồn tại hay không. Trang đăng nhập đã
    # cẩn thận để không thành công cụ dò email; để lộ ở đây thì công cốc.
    return RedirectResponse("/quen-mat-khau?da_gui=1", status_code=303)


@router.get("/dat-lai-mat-khau", response_class=HTMLResponse, name="reset_form")
def reset_form(request: Request, token: str = "", loi: str = "", db: Session = Depends(get_db)):
    return templates.TemplateResponse(
        request,
        "auth/dat_lai_mat_khau.html",
        {
            "user": None,
            "token": token,
            "hop_le": doc_ve(db, token) is not None,
            "loi": message_for(loi),
        },
    )


@router.post("/dat-lai-mat-khau")
def reset_submit(
    request: Request,
    token: str = Form(""),
    mat_khau: str = Form(""),
    mat_khau_lai: str = Form(""),
    db: Session = Depends(get_db),
):
    ve = doc_ve(db, token)
    if ve is None:
        return RedirectResponse("/dat-lai-mat-khau?loi=ve_hong", status_code=303)
    if (problem := check_password(mat_khau)) is not None:
        return RedirectResponse(
            f"/dat-lai-mat-khau?token={token}&loi={problem}", status_code=303
        )
    if mat_khau_lai != mat_khau:
        return RedirectResponse(
            f"/dat-lai-mat-khau?token={token}&loi=mat_khau_lech", status_code=303
        )

    user = dat_lai(db, ve, mat_khau)
    # Đăng nhập lại ngay với cookie mang dấu thời gian mới; mọi cookie cũ vừa
    # hết giá trị, kể cả cookie đang nằm trong tay người chiếm tài khoản.
    return _signed_in(request, user, _home_for(user))


@router.get("/dang-nhap/{provider}")
async def oauth_start(provider: str, request: Request):
    if not oauth_bat(provider):
        return RedirectResponse("/dang-nhap", status_code=303)
    khach_oauth = oauth_khach()
    redirect_uri = str(request.url_for("oauth_callback", provider=provider))
    return await getattr(khach_oauth, provider).authorize_redirect(request, redirect_uri)


@router.get("/dang-nhap/{provider}/callback", name="oauth_callback")
async def oauth_finish(provider: str, request: Request, db: Session = Depends(get_db)):
    if not oauth_bat(provider):
        return RedirectResponse("/dang-nhap", status_code=303)

    from authlib.integrations.starlette_client import OAuthError

    try:
        token = await getattr(oauth_khach(), provider).authorize_access_token(request)
    except OAuthError:
        # Người dùng bấm huỷ, hoặc state không khớp. Không có gì để nói thêm.
        return RedirectResponse("/dang-nhap?loi=sai_thong_tin", status_code=303)

    info = doc_userinfo(token.get("userinfo") or {})
    if info is None:
        return RedirectResponse("/dang-nhap?loi=sai_thong_tin", status_code=303)

    # Tài khoản bị đình chỉ vẫn đăng nhập được; chặn nằm ở cửa /giao-vien, để
    # người dùng đọc được lý do thay vì bị đá ra không lời giải thích.
    user = noi_tai_khoan(db, provider, info)
    return _signed_in(request, user, _home_for(user))


@router.get("/dang-ky/giao-vien", response_class=HTMLResponse)
def teacher_signup_form(request: Request, loi: str = "", db: Session = Depends(get_db)):
    return templates.TemplateResponse(
        request,
        "auth/signup_giao_vien.html",
        {"user": None, "loi": message_for(loi), "truong": truong_dang_nhan(db)},
    )


@router.post("/dang-ky/giao-vien")
def teacher_signup_submit(
    request: Request,
    ten: str = Form(""),
    truong_id: str = Form(""),
    ma_truong: str = Form(""),
    email: str = Form(""),
    mat_khau: str = Form(""),
    mat_khau_lai: str = Form(""),
    dong_y: str = Form(""),
    db: Session = Depends(get_db),
):
    def back(loi: str) -> RedirectResponse:
        return RedirectResponse(f"/dang-ky/giao-vien?loi={loi}", status_code=303)

    # Mã trường là cánh cửa duy nhất dẫn tới tài khoản giáo viên, nên nó phải
    # được đếm số lần thử như mật khẩu. Hạn ba ngày chẳng giúp gì nếu mã dò
    # được trong một buổi chiều.
    key = f"gv:ip:{_client_ip(request)}"
    if throttle.blocked(key):
        return back("thu_lai_sau")

    name, problem = clean_name(ten)
    if problem:
        return back(problem)

    try:
        school_id = int(truong_id)
    except (TypeError, ValueError):
        return back("truong_sai")

    truong = truong_theo_ma(db, school_id, ma_truong)
    if truong is None:
        throttle.record_failure(key)
        return back("ma_giao_vien_sai")

    address = normalise_email(email)
    if email_looks_wrong(address):
        return back("email_hong")
    if email_taken(db, address):
        return back("email_trung")
    if (problem := check_password(mat_khau)) is not None:
        return back(problem)
    if mat_khau_lai != mat_khau:
        return back("mat_khau_lech")

    if not dong_y:
        return back("chua_dong_y")

    throttle.clear(key)
    user = create_user(
        db,
        name=name,
        email=address,
        password=mat_khau,
        role="teacher",
        school_id=truong.id,
    )
    _ghi_dong_y(db, user)
    return _signed_in(request, user, "/giao-vien")


@router.get("/chon-avatar", response_class=HTMLResponse)
def avatar_form(
    request: Request,
    ma_lop: str = "",
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    klass = None
    if user is not None:
        membership = (
            db.query(Class)
            .join(ClassMembership, ClassMembership.class_id == Class.id)
            .filter(ClassMembership.student_id == user.id)
            .first()
        )
        klass = membership
    elif ma_lop:
        klass = db.query(Class).filter(Class.class_code == ma_lop.upper()).first()
    return templates.TemplateResponse(
        request,
        "auth/avatar.html",
        {"user": user, "avatars": AVATARS, "ma_lop": ma_lop, "klass": klass},
    )


@router.post("/chon-avatar")
def avatar_submit(
    request: Request,
    avatar_id: str = Form("avatar-1"),
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user is None:
        return RedirectResponse("/dang-ky", status_code=303)
    if avatar_id in AVATAR_EMOJI:
        user.avatar_id = avatar_id
        db.commit()
    return RedirectResponse(_home_for(user), status_code=303)


@router.get("/dang-xuat")
def logout():
    response = RedirectResponse("/", status_code=303)
    clear_session(response)
    return response
