"""Chọn không gian làm việc trước khi vào bảng điều khiển."""

from __future__ import annotations

from app import boi_canh
from app.db import SessionLocal
from app.models import Class, ClassMembership, User
from tests.du_lieu_mau import SEED_EMAILS, SEED_PASSWORD
from tests.conftest import login_independent, login_student, login_teacher


def _vao_khong_chon(client, key: str = "hoc_sinh_co_lop"):
    """Đăng nhập nhưng cố tình không chọn bối cảnh."""
    client.post(
        "/dang-nhap",
        data={"email": SEED_EMAILS[key], "mat_khau": SEED_PASSWORD},
        follow_redirects=False,
    )


def test_a_student_in_a_class_is_asked_before_the_dashboard_opens(client):
    _vao_khong_chon(client)
    r = client.get("/trang-ca-nhan", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/chon-khong-gian"


def test_the_picker_offers_the_class_and_personal_work(client):
    _vao_khong_chon(client)
    page = client.get("/chon-khong-gian").text
    assert "11A2" in page
    assert "Việc cá nhân" in page


def test_choosing_is_remembered_so_the_question_comes_once(client):
    _vao_khong_chon(client)
    client.post("/chon-khong-gian", data={"khoa": "ca-nhan"}, follow_redirects=False)
    assert client.get("/trang-ca-nhan", follow_redirects=False).status_code == 200
    assert client.get("/trang-ca-nhan", follow_redirects=False).status_code == 200


def test_a_student_with_no_class_is_never_asked(client):
    """Một lựa chọn thì câu hỏi chỉ làm phiền."""
    login_independent(client)
    assert client.get("/trang-ca-nhan", follow_redirects=False).status_code == 200


def test_personal_work_hides_class_assignments_and_notices(client):
    login_student(client)
    co_lop = client.get("/trang-ca-nhan").text

    client.post("/chon-khong-gian", data={"khoa": "ca-nhan"}, follow_redirects=False)
    ca_nhan = client.get("/trang-ca-nhan").text

    # Thông báo của lớp 11A2 chỉ có ở bối cảnh lớp.
    assert "lớp 11A2" in co_lop
    assert "lớp 11A2" not in ca_nhan


def test_a_class_you_do_not_belong_to_cannot_be_chosen(client):
    """Giá trị duy nhất người dùng bịa được là số hiệu lớp, nên nó phải được
    đối chiếu lại với danh sách lớp thật."""
    _vao_khong_chon(client)
    db = SessionLocal()
    try:
        khong_thuoc = (
            db.query(Class).filter(Class.class_code == "GALS-10B1").first()
        )
    finally:
        db.close()

    r = client.post(
        "/chon-khong-gian",
        data={"khoa": f"lop:{khong_thuoc.id}"},
        follow_redirects=False,
    )
    assert r.headers["location"] == "/chon-khong-gian"


def test_a_nonsense_key_is_refused(client):
    _vao_khong_chon(client)
    r = client.post("/chon-khong-gian", data={"khoa": "lop:999999"}, follow_redirects=False)
    assert r.headers["location"] == "/chon-khong-gian"


def test_leaving_a_class_falls_back_instead_of_breaking(client):
    """Cookie cũ trỏ vào một lớp không còn thuộc về mình thì rơi về mặc định."""
    login_student(client)
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == SEED_EMAILS["hoc_sinh_co_lop"]).first()
        db.query(ClassMembership).filter(ClassMembership.student_id == user.id).delete()
        db.commit()
    finally:
        db.close()

    assert client.get("/trang-ca-nhan", follow_redirects=False).status_code == 200


def test_the_header_shows_which_space_you_are_in(client):
    login_student(client)
    page = client.get("/trang-ca-nhan").text
    assert "Không gian hiện tại" in page
    assert "/chon-khong-gian" in page


def test_the_switcher_is_hidden_when_there_is_nothing_to_switch(client):
    login_independent(client)
    assert "Không gian hiện tại" not in client.get("/trang-ca-nhan").text


def test_a_teacher_gets_all_classes_plus_each_one(client):
    login_teacher(client)
    page = client.get("/chon-khong-gian").text
    assert "Tất cả lớp" in page
    assert "11A2" in page
    assert "10B1" in page


def test_a_teacher_is_not_stopped_at_the_picker(client):
    """Trang giáo viên đã có bộ lọc ?lop= riêng, nên mặc định "Tất cả lớp" là
    đúng hành vi cũ; bắt chọn thêm chỉ là một bước thừa."""
    client.post(
        "/dang-nhap",
        data={"email": SEED_EMAILS["giao_vien"], "mat_khau": SEED_PASSWORD},
        follow_redirects=False,
    )
    assert client.get("/giao-vien", follow_redirects=False).status_code == 200


def test_the_default_for_a_student_is_personal_work(client):
    db = SessionLocal()
    try:
        trang = db.query(User).filter(User.email == SEED_EMAILS["hoc_sinh_doc_lap"]).first()
        assert boi_canh.mac_dinh(db, trang).la_ca_nhan
    finally:
        db.close()
