"""Trang chủ, đăng ký, đăng nhập, chọn avatar, đăng xuất.

Xác thực là giả lập (§6): mọi email/mật khẩu đều vào tài khoản học sinh mặc
định. Các màn hình đăng ký / nhập mã lớp / chọn avatar vẫn được dựng và bấm
được theo sơ đồ, nhưng không lưu gì thật.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.auth import (
    DEFAULT_STUDENT_EMAIL,
    DEMO_ACCOUNTS,
    clear_session,
    get_current_user,
    set_session,
)
from app.db import get_db
from app.models import Class, User
from app.scenarios import all_scenarios
from app.templating import templates

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


def _login_as(email: str, db: Session, destination: str) -> RedirectResponse:
    user = db.query(User).filter(User.email == email).first()
    if user is None:  # phòng khi dữ liệu gieo bị đổi
        user = db.query(User).filter(User.role == "student").first()
    response = RedirectResponse(destination, status_code=303)
    set_session(response, user.id)
    return response


@router.get("/", response_class=HTMLResponse)
def landing(request: Request, user: User | None = Depends(get_current_user)):
    return templates.TemplateResponse(
        request,
        "auth/landing.html",
        {"user": None, "logged_in": user is not None, "scenarios": all_scenarios()},
    )


@router.get("/dang-nhap", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse(request, "auth/login.html", {"user": None})


@router.post("/dang-nhap")
def login_submit(
    request: Request,
    email: str = Form(""),
    mat_khau: str = Form(""),
    db: Session = Depends(get_db),
):
    # Giả lập: bất kỳ thông tin nào cũng vào tài khoản học sinh mặc định.
    return _login_as(DEFAULT_STUDENT_EMAIL, db, "/trang-ca-nhan")


@router.get("/dang-ky", response_class=HTMLResponse)
def signup_form(request: Request):
    return templates.TemplateResponse(request, "auth/signup.html", {"user": None})


@router.post("/dang-ky")
def signup_submit(request: Request, ma_lop: str = Form("")):
    # Không lưu gì thật — chuyển sang bước chọn avatar theo sơ đồ.
    target = "/chon-avatar"
    if ma_lop.strip():
        target += f"?ma_lop={ma_lop.strip()}"
    return RedirectResponse(target, status_code=303)


@router.get("/chon-avatar", response_class=HTMLResponse)
def avatar_form(request: Request, ma_lop: str = "", db: Session = Depends(get_db)):
    klass = None
    if ma_lop:
        klass = db.query(Class).filter(Class.class_code == ma_lop.upper()).first()
    return templates.TemplateResponse(
        request,
        "auth/avatar.html",
        {"user": None, "avatars": AVATARS, "ma_lop": ma_lop, "klass": klass},
    )


@router.post("/chon-avatar")
def avatar_submit(
    request: Request,
    avatar_id: str = Form("avatar-1"),
    ma_lop: str = Form(""),
    db: Session = Depends(get_db),
):
    # Đăng ký không tạo tài khoản thật; đưa về tài khoản demo tương ứng.
    email = (
        DEMO_ACCOUNTS["hoc_sinh_co_lop"] if ma_lop.strip() else DEMO_ACCOUNTS["hoc_sinh_doc_lap"]
    )
    user = db.query(User).filter(User.email == email).first()
    if user and avatar_id in AVATAR_EMOJI:
        user.avatar_id = avatar_id  # avatar vừa chọn có hiệu lực ngay, cho demo
        db.commit()
    return _login_as(email, db, "/trang-ca-nhan")


@router.get("/demo/{account}")
def demo_login(account: str, db: Session = Depends(get_db)):
    """Ba nút 'Demo nhanh' — mở thẳng từng đường vào sản phẩm."""
    email = DEMO_ACCOUNTS.get(account)
    if email is None:
        return RedirectResponse("/dang-nhap", status_code=303)
    destination = "/giao-vien" if account == "giao_vien" else "/trang-ca-nhan"
    return _login_as(email, db, destination)


@router.get("/dang-xuat")
def logout():
    response = RedirectResponse("/", status_code=303)
    clear_session(response)
    return response
