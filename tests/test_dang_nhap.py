"""Đăng ký và đăng nhập thật.

Trước đây biểu mẫu đăng nhập bỏ qua cả email lẫn mật khẩu, còn biểu mẫu đăng
ký thu ba trường rồi vứt cả ba. Những bài dưới đây khoá lại từng điều mà chỗ
mới phải giữ.
"""

from __future__ import annotations

from app import throttle
from app.db import SessionLocal
from app.models import Class, ClassMembership, User
from tests.du_lieu_mau import SEED_EMAILS, SEED_PASSWORD
from app.security import hash_password
from tests.conftest import login_student

MAT_KHAU = "chuoi-dai-du-8"


def _dang_ky(client, **ghi_de):
    data = {
        "ten": "Ngô Bảo Châu",
        "email": "chau@example.com",
        "mat_khau": MAT_KHAU,
        "tuoi": "17",
        "ma_lop": "",
        "dong_y": "1",
    }
    data.update(ghi_de)
    return client.post("/dang-ky", data=data, follow_redirects=False)


def _user(email: str) -> User | None:
    db = SessionLocal()
    try:
        return db.query(User).filter(User.email == email).first()
    finally:
        db.close()


def test_signup_creates_an_account_and_signs_it_in(client):
    r = _dang_ky(client)
    assert r.status_code == 303
    assert r.headers["location"] == "/chon-avatar"

    user = _user("chau@example.com")
    assert user is not None
    assert user.name == "Ngô Bảo Châu"
    assert user.role == "student"
    # Đã đăng nhập ngay, không phải quay lại gõ mật khẩu.
    assert client.get("/trang-ca-nhan").status_code == 200


def test_the_password_is_never_stored_as_typed(client):
    _dang_ky(client)
    user = _user("chau@example.com")
    assert user.password_hash
    assert MAT_KHAU not in user.password_hash
    assert user.password_hash.startswith("$argon2")


def test_email_is_lowercased_so_one_person_cannot_hold_two_accounts(client):
    _dang_ky(client, email="  CHAU@Example.COM ")
    assert _user("chau@example.com") is not None


def test_a_taken_email_is_refused_and_says_so(client):
    _dang_ky(client)
    r = _dang_ky(client, ten="Người khác")
    assert "loi=email_trung" in r.headers["location"]


def test_a_short_password_is_refused(client):
    r = _dang_ky(client, mat_khau="ngan")
    assert "loi=mat_khau_ngan" in r.headers["location"]
    assert _user("chau@example.com") is None


def test_a_name_the_filter_blocks_never_becomes_an_account(client):
    r = _dang_ky(client, ten="đm thằng ngu")
    assert "loi=ten_bi_chan" in r.headers["location"]
    assert _user("chau@example.com") is None


def test_the_error_redirect_carries_a_code_not_a_sentence(client):
    """Chỗ cũ nhét cả câu trả lời của bộ lọc vào URL. Câu trả lời cho trường
    hợp khủng hoảng dài mấy trăm ký tự, có xuống dòng và có số 111 — vừa hỏng
    header, vừa đem lời nhắn đó đi dán cạnh ô nhập tên."""
    r = _dang_ky(client, ten="tôi muốn chết")
    location = r.headers["location"]
    assert "111" not in location
    assert "\n" not in location
    assert len(location) < 80


def test_under_sixteen_without_a_class_code_gets_the_school_route(client):
    r = _dang_ky(client, tuoi="14")
    assert r.headers["location"] == "/dang-ky/can-ma-lop"
    assert _user("chau@example.com") is None

    page = client.get("/dang-ky/can-ma-lop").text
    assert "mã lớp" in page.lower()
    # Trang phải nói rõ vì sao, chứ không chỉ chặn.
    assert "nhà trường" in page


def test_under_sixteen_with_a_real_class_code_is_allowed_through(client):
    """Qua lớp thì nhà trường là bên đứng ra xin phép gia đình, nên đường này mở."""
    r = _dang_ky(client, tuoi="14", ma_lop="GALS-11A2")
    assert r.headers["location"] == "/chon-avatar"
    assert _user("chau@example.com") is not None


def test_a_class_code_that_matches_nothing_is_refused(client):
    r = _dang_ky(client, ma_lop="GALS-KHONG-CO")
    assert "loi=ma_lop_sai" in r.headers["location"]
    assert _user("chau@example.com") is None


def test_a_valid_class_code_joins_the_class(client):
    _dang_ky(client, ma_lop="GALS-11A2")
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "chau@example.com").first()
        klass = db.query(Class).filter(Class.class_code == "GALS-11A2").first()
        joined = (
            db.query(ClassMembership)
            .filter(
                ClassMembership.student_id == user.id,
                ClassMembership.class_id == klass.id,
            )
            .first()
        )
        assert joined is not None
    finally:
        db.close()


def test_login_needs_the_real_password(client):
    r = client.post(
        "/dang-nhap",
        data={"email": SEED_EMAILS["hoc_sinh_co_lop"], "mat_khau": "sai-be-bet"},
        follow_redirects=False,
    )
    assert "loi=sai_thong_tin" in r.headers["location"]
    assert client.get("/trang-ca-nhan", follow_redirects=False).status_code == 303


def test_an_unknown_email_and_a_wrong_password_look_identical(client):
    """Nếu hai trường hợp trả lời khác nhau thì trang đăng nhập trở thành công
    cụ dò xem email nào đã đăng ký."""
    khong_co = client.post(
        "/dang-nhap",
        data={"email": "khong-ai@example.com", "mat_khau": "sai-be-bet"},
        follow_redirects=False,
    )
    sai_mat_khau = client.post(
        "/dang-nhap",
        data={"email": SEED_EMAILS["hoc_sinh_co_lop"], "mat_khau": "sai-be-bet"},
        follow_redirects=False,
    )
    assert khong_co.headers["location"] == sai_mat_khau.headers["location"]


def test_a_teacher_lands_on_the_teacher_home(client):
    r = client.post(
        "/dang-nhap",
        data={"email": SEED_EMAILS["giao_vien"], "mat_khau": SEED_PASSWORD},
        follow_redirects=False,
    )
    assert r.headers["location"] == "/giao-vien"


def test_login_stamps_the_time_so_a_dormant_account_is_visible(client):
    assert _user(SEED_EMAILS["hoc_sinh_co_lop"]).last_login_at is None
    login_student(client)
    assert _user(SEED_EMAILS["hoc_sinh_co_lop"]).last_login_at is not None


def test_an_outdated_hash_is_upgraded_on_the_way_in(client):
    """Đăng nhập là dịp duy nhất nâng tham số Argon2 mà không cần biết mật khẩu
    gốc — chỉ lúc đó mới có bản rõ trong tay."""
    from argon2 import PasswordHasher

    yeu = PasswordHasher(time_cost=1, memory_cost=8, parallelism=1)
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == SEED_EMAILS["hoc_sinh_co_lop"]).first()
        user.password_hash = yeu.hash(SEED_PASSWORD)
        cu = user.password_hash
        db.commit()
    finally:
        db.close()

    login_student(client)
    assert _user(SEED_EMAILS["hoc_sinh_co_lop"]).password_hash != cu


def test_repeated_wrong_passwords_get_locked_out(client):
    for _ in range(throttle.MAX_ATTEMPTS):
        client.post(
            "/dang-nhap",
            data={"email": SEED_EMAILS["hoc_sinh_co_lop"], "mat_khau": "sai"},
            follow_redirects=False,
        )
    # Đúng mật khẩu cũng không vào được nữa, vì đã bị khoá.
    r = client.post(
        "/dang-nhap",
        data={"email": SEED_EMAILS["hoc_sinh_co_lop"], "mat_khau": SEED_PASSWORD},
        follow_redirects=False,
    )
    assert "loi=thu_lai_sau" in r.headers["location"]


def test_a_correct_login_clears_the_counter(client):
    client.post(
        "/dang-nhap",
        data={"email": SEED_EMAILS["hoc_sinh_co_lop"], "mat_khau": "sai"},
        follow_redirects=False,
    )
    login_student(client)
    assert not throttle.blocked(f"dn:email:{SEED_EMAILS['hoc_sinh_co_lop']}")


def test_an_account_with_no_password_cannot_be_entered_with_a_blank_one(client):
    """Tài khoản đăng nhập bằng Google chưa từng đặt mật khẩu. Gửi chuỗi rỗng
    không được coi là khớp."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == SEED_EMAILS["hoc_sinh_doc_lap"]).first()
        user.password_hash = None
        db.commit()
    finally:
        db.close()

    r = client.post(
        "/dang-nhap",
        data={"email": SEED_EMAILS["hoc_sinh_doc_lap"], "mat_khau": ""},
        follow_redirects=False,
    )
    assert "loi=sai_thong_tin" in r.headers["location"]


def test_the_avatar_step_sets_the_avatar_on_the_new_account(client):
    _dang_ky(client)
    client.post("/chon-avatar", data={"avatar_id": "avatar-7"}, follow_redirects=False)
    assert _user("chau@example.com").avatar_id == "avatar-7"


def test_the_avatar_step_needs_an_account(client):
    r = client.post("/chon-avatar", data={"avatar_id": "avatar-7"}, follow_redirects=False)
    assert r.headers["location"] == "/dang-ky"


def test_the_shortcut_that_logged_anyone_in_is_gone(client):
    """/demo/{tài khoản} cho quyền giáo viên đầy đủ mà không cần bất cứ thứ gì."""
    for account in ["giao_vien", "hoc_sinh_co_lop", "hoc_sinh_doc_lap"]:
        assert client.get(f"/demo/{account}").status_code == 404
    assert client.get("/giao-vien", follow_redirects=False).status_code == 303


def test_no_page_still_offers_a_one_click_login(client):
    for url in ["/", "/dang-nhap", "/dang-ky", "/kham-pha", "/ve-chung-toi"]:
        assert "/demo/" not in client.get(url).text, url


def test_the_seed_password_cannot_reach_a_real_database(monkeypatch):
    """Mật khẩu mẫu nằm công khai trong mã nguồn. Thứ giữ cho nó không lên
    Postgres phải là mã, không phải trí nhớ của người deploy."""
    import pytest

    import tests.du_lieu_mau as seed

    monkeypatch.setattr(seed, "is_sqlite", False)
    with pytest.raises(RuntimeError, match="SQLite"):
        seed._refuse_people_on_a_real_database()


def test_hashing_the_same_password_twice_gives_different_hashes():
    """Argon2 tự thêm muối. Hai hàng giống nhau trong bảng sẽ để lộ hai người
    dùng chung mật khẩu."""
    assert hash_password("cung-mot-mat-khau") != hash_password("cung-mot-mat-khau")
