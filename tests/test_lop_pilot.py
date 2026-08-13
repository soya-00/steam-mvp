"""Những việc người dùng phải tự làm được trước khi có người thật dùng.

Ba trong số này là lời hứa đã in trong văn bản pháp lý mà mã chưa làm được:
đổi mật khẩu (Điều khoản 2.4), rời lớp để rút lại đồng ý (Chính sách 9.1), và
vào lớp sau khi đã có tài khoản (trang chọn ảnh đại diện).
"""

from __future__ import annotations

from app.db import SessionLocal
from app.lop import ma_lop_moi
from app.models import Class, ClassMembership, User
from app.seed import SEED_EMAILS, SEED_PASSWORD
from tests.conftest import login_independent, login_student, login_teacher

MOI = "mat-khau-moi-1"


def _user(email: str) -> User:
    db = SessionLocal()
    try:
        return db.query(User).filter(User.email == email).first()
    finally:
        db.close()


def _lop(ma: str = "GALS-11A2") -> Class:
    db = SessionLocal()
    try:
        return db.query(Class).filter(Class.class_code == ma).first()
    finally:
        db.close()


def _o_trong_lop(email: str, class_id: int) -> bool:
    db = SessionLocal()
    try:
        u = db.query(User).filter(User.email == email).first()
        return (
            db.query(ClassMembership)
            .filter(
                ClassMembership.student_id == u.id,
                ClassMembership.class_id == class_id,
            )
            .first()
            is not None
        )
    finally:
        db.close()


# ---------------------------------------------------------------- đổi mật khẩu

def test_a_signed_in_user_can_change_their_password(client):
    login_student(client)
    client.post(
        "/tai-khoan/mat-khau",
        data={"mat_khau_cu": SEED_PASSWORD, "mat_khau_moi": MOI},
    )
    client.get("/dang-xuat")
    r = client.post(
        "/dang-nhap",
        data={"email": SEED_EMAILS["hoc_sinh_co_lop"], "mat_khau": MOI},
        follow_redirects=False,
    )
    assert "loi=" not in r.headers["location"]


def test_changing_a_password_needs_the_current_one(client):
    """Không có bước này thì ai mượn được máy đang mở sẵn cũng chiếm được tài
    khoản vĩnh viễn."""
    login_student(client)
    r = client.post(
        "/tai-khoan/mat-khau",
        data={"mat_khau_cu": "doan-bua", "mat_khau_moi": MOI},
        follow_redirects=False,
    )
    assert "loi=mat_khau_cu_sai" in r.headers["location"]

    client.get("/dang-xuat")
    van_vao_duoc = client.post(
        "/dang-nhap",
        data={"email": SEED_EMAILS["hoc_sinh_co_lop"], "mat_khau": SEED_PASSWORD},
        follow_redirects=False,
    )
    assert "loi=" not in van_vao_duoc.headers["location"]


def test_a_weak_new_password_is_refused(client):
    login_student(client)
    r = client.post(
        "/tai-khoan/mat-khau",
        data={"mat_khau_cu": SEED_PASSWORD, "mat_khau_moi": "ngan"},
        follow_redirects=False,
    )
    assert "loi=mat_khau_ngan" in r.headers["location"]


def test_changing_a_password_evicts_every_other_device(client, client_tho):
    """Đây là lý do chính của chức năng này: đuổi người đang giữ phiên."""
    login_student(client)

    # Thiết bị thứ hai, cùng tài khoản. Dùng client trần để giữ nguyên cookie
    # cũ sau khi thiết bị kia đổi mật khẩu.
    client_tho.get("/")
    ve = client_tho.cookies.get("gals_csrf")
    client_tho.post(
        "/dang-nhap",
        data={"_csrf": ve, "email": SEED_EMAILS["hoc_sinh_co_lop"],
              "mat_khau": SEED_PASSWORD},
        follow_redirects=False,
    )
    assert client_tho.get("/trang-ca-nhan", follow_redirects=False).status_code in (200, 303)

    client.post(
        "/tai-khoan/mat-khau",
        data={"mat_khau_cu": SEED_PASSWORD, "mat_khau_moi": MOI},
    )

    # Thiết bị kia giữ cookie cũ, giờ vô giá trị.
    assert client_tho.get("/trang-ca-nhan", follow_redirects=False).status_code == 303
    # Còn người vừa đổi thì vẫn đang đăng nhập, không tự đá mình ra.
    assert client.get("/tai-khoan", follow_redirects=False).status_code == 200


# --------------------------------------------------------------------- vào lớp

def test_joining_shows_a_confirmation_before_anything_changes(client):
    """Vào lớp là thao tác duy nhất đổi chuyện ai đọc được bài của mình, nên nó
    không phải một nút bấm cái xong."""
    login_independent(client)
    page = client.get("/tai-khoan/vao-lop?ma=GALS-11A2").text

    assert "11A2" in page
    assert "Cô Mai" in page
    assert "đọc được phần bạn nộp" in page
    # Chưa vào lớp chỉ vì mở trang xem.
    assert not _o_trong_lop(SEED_EMAILS["hoc_sinh_doc_lap"], _lop().id)


def test_confirming_actually_joins(client):
    login_independent(client)
    client.post("/tai-khoan/vao-lop", data={"ma": "GALS-11A2"})
    assert _o_trong_lop(SEED_EMAILS["hoc_sinh_doc_lap"], _lop().id)


def test_joining_twice_does_not_duplicate_the_row(client):
    login_independent(client)
    client.post("/tai-khoan/vao-lop", data={"ma": "GALS-11A2"})
    client.post("/tai-khoan/vao-lop", data={"ma": "GALS-11A2"})

    db = SessionLocal()
    try:
        u = db.query(User).filter(User.email == SEED_EMAILS["hoc_sinh_doc_lap"]).first()
        assert db.query(ClassMembership).filter(
            ClassMembership.student_id == u.id
        ).count() == 1
    finally:
        db.close()


def test_a_bad_code_says_so_and_joins_nothing(client):
    login_independent(client)
    r = client.post("/tai-khoan/vao-lop", data={"ma": "GALS-KHONG-CO"},
                    follow_redirects=False)
    assert "loi=ma_lop_sai" in r.headers["location"]


def test_a_closed_class_no_longer_admits_anyone(client):
    db = SessionLocal()
    try:
        from app.lop import dong_lop
        dong_lop(db, db.query(Class).filter(Class.class_code == "GALS-11A2").first())
    finally:
        db.close()

    login_independent(client)
    r = client.post("/tai-khoan/vao-lop", data={"ma": "GALS-11A2"}, follow_redirects=False)
    assert "loi=ma_lop_sai" in r.headers["location"]


# --------------------------------------------------------------------- rời lớp

def test_leaving_takes_effect_immediately(client):
    """Chính sách 9.1 gọi đây là cách rút lại đồng ý. Quyền phải xin phép mới
    dùng được thì không còn là quyền."""
    login_student(client)
    lop_id = _lop().id
    assert _o_trong_lop(SEED_EMAILS["hoc_sinh_co_lop"], lop_id)

    client.post(f"/tai-khoan/roi-lop/{lop_id}", data={})
    assert not _o_trong_lop(SEED_EMAILS["hoc_sinh_co_lop"], lop_id)


def test_leaving_keeps_every_row_the_student_wrote(client):
    from app.models import Badge, JournalEntry, PortfolioEntry

    login_student(client)
    uid = _user(SEED_EMAILS["hoc_sinh_co_lop"]).id

    db = SessionLocal()
    try:
        truoc = (
            db.query(JournalEntry).filter(JournalEntry.student_id == uid).count(),
            db.query(PortfolioEntry).filter(PortfolioEntry.student_id == uid).count(),
            db.query(Badge).filter(Badge.student_id == uid).count(),
        )
    finally:
        db.close()

    client.post(f"/tai-khoan/roi-lop/{_lop().id}", data={})

    db = SessionLocal()
    try:
        sau = (
            db.query(JournalEntry).filter(JournalEntry.student_id == uid).count(),
            db.query(PortfolioEntry).filter(PortfolioEntry.student_id == uid).count(),
            db.query(Badge).filter(Badge.student_id == uid).count(),
        )
    finally:
        db.close()
    assert sau == truoc and truoc[0] > 0


def test_after_leaving_the_teacher_cannot_reach_that_student(client, client_tho):
    """Kiểm cả bốn cửa, không chỉ danh sách lớp."""
    login_student(client)
    uid = _user(SEED_EMAILS["hoc_sinh_co_lop"]).id
    lop_id = _lop().id
    client.post(f"/tai-khoan/roi-lop/{lop_id}", data={})

    client_tho.get("/")
    ve = client_tho.cookies.get("gals_csrf")
    client_tho.post("/dang-nhap", data={"_csrf": ve, "email": SEED_EMAILS["giao_vien"],
                                        "mat_khau": SEED_PASSWORD}, follow_redirects=False)

    # Đối chiếu bằng tên, không bằng số hiệu: chuỗi "2" nằm sẵn trong "11A2".
    assert "Nguyễn Khánh Linh" not in client_tho.get(f"/giao-vien/lop/{lop_id}").text
    assert client_tho.get(f"/giao-vien/hoc-sinh/{uid}",
                          follow_redirects=False).status_code == 303
    nhan_xet = client_tho.post(
        f"/giao-vien/hoc-sinh/{uid}/nhan-xet",
        data={"_csrf": ve, "noi_dung": "thử"},
        follow_redirects=False,
    )
    assert nhan_xet.status_code in (303, 403)

    zip_bytes = client_tho.get("/tai-khoan/du-lieu").content
    import io
    import zipfile

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        noi_dung = b"".join(z.read(n) for n in z.namelist())
    assert "Nguyễn Khánh Linh".encode() not in noi_dung


def test_leaving_a_class_you_are_not_in_is_harmless(client):
    login_independent(client)
    r = client.post(f"/tai-khoan/roi-lop/{_lop().id}", data={}, follow_redirects=False)
    assert r.status_code == 303


# ------------------------------------------------------------------ mã lớp mới

def test_generated_class_codes_are_always_checked_for_collisions():
    """Chỗ cũ thử 50 lần rồi trả về một mã 6 ký tự **không kiểm trùng**, nên khi
    trùng thì giáo viên gặp lỗi 500 lúc tạo lớp."""
    db = SessionLocal()
    try:
        da_co = {c.class_code for c in db.query(Class).all()}
        for _ in range(30):
            ma = ma_lop_moi(db)
            assert ma not in da_co
            assert ma.startswith("GALS-")
    finally:
        db.close()


# ------------------------------------------------------------- máy quét, noindex

def test_a_shared_portfolio_asks_search_engines_to_stay_out(client):
    login_student(client)
    trang = client.get("/ho-so/chia-se").text
    import re

    token = re.search(r'/p/([A-Za-z0-9_.\-]+)', trang)
    assert token, "không tìm thấy đường dẫn chia sẻ"

    page = client.get(f"/p/{token.group(1)}").text
    assert 'name="robots"' in page
    assert "noindex" in page


def test_ordinary_pages_carry_no_noindex(client):
    login_student(client)
    for url in ["/", "/kham-pha", "/trang-ca-nhan"]:
        assert "noindex" not in client.get(url).text, url


def test_robots_txt_is_served_from_the_root(client):
    """Máy quét tìm /robots.txt, không tìm /static/robots.txt."""
    r = client.get("/robots.txt")
    assert r.status_code == 200
    assert "Disallow: /p/" in r.text


# ------------------------------------------------------- không còn lời hứa suông

def test_the_account_page_offers_the_controls_it_describes(client):
    login_student(client)
    page = client.get("/tai-khoan").text
    assert "/tai-khoan/roi-lop/" in page
    assert "/tai-khoan/vao-lop" in page
    assert "/tai-khoan/mat-khau" in page


def test_the_avatar_step_no_longer_promises_a_missing_feature(client):
    page = client.get("/chon-avatar?ma_lop=KHONG-CO-THAT").text
    assert "tham gia lớp sau cũng không sao" not in page
