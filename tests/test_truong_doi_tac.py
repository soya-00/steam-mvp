"""Tài khoản giáo viên đi qua trường đối tác.

Tài khoản giáo viên là tài khoản đọc được nhật ký của trẻ. Thứ canh nó không
phải ô chọn trường — ai cũng chọn được — mà là mã của trường, và mã đó sống
ba ngày.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from app import throttle
from app.db import SessionLocal
from app.models import Class, School, User
from app.schools import cap_ma_moi, ma_con_han, sinh_ma
from app.seed import SEED_EMAILS, SEED_PASSWORD

MAT_KHAU = "chuoi-dai-du-8"


def _truong(**ghi_de) -> int:
    db = SessionLocal()
    try:
        t = db.query(School).first()
        for k, v in ghi_de.items():
            setattr(t, k, v)
        db.commit()
        return t.id
    finally:
        db.close()


def _dang_ky_gv(client, **ghi_de):
    db = SessionLocal()
    try:
        t = db.query(School).first()
        data = {
            "ten": "Thầy Nam",
            "truong_id": str(t.id),
            "ma_truong": t.ma_giao_vien or "",
            "email": "nam@truong.edu.vn",
            "mat_khau": MAT_KHAU,
        }
    finally:
        db.close()
    data.update(ghi_de)
    return client.post("/dang-ky/giao-vien", data=data, follow_redirects=False)


def _user(email: str) -> User | None:
    db = SessionLocal()
    try:
        return db.query(User).filter(User.email == email).first()
    finally:
        db.close()


def test_a_correct_code_creates_an_active_teacher(client):
    r = _dang_ky_gv(client)
    assert r.headers["location"] == "/giao-vien"

    gv = _user("nam@truong.edu.vn")
    assert gv is not None
    assert gv.role == "teacher"
    assert gv.status == "hoat_dong"
    assert gv.school_id is not None
    assert client.get("/giao-vien").status_code == 200


def test_a_wrong_code_creates_nothing(client):
    r = _dang_ky_gv(client, ma_truong="SAIBETBET")
    assert "loi=ma_giao_vien_sai" in r.headers["location"]
    assert _user("nam@truong.edu.vn") is None


def test_a_code_one_moment_past_its_expiry_creates_nothing(client):
    """Cửa sổ ba ngày tự đóng, không cần tác vụ nền nào dọn dẹp."""
    _truong(ma_het_han=datetime.now() - timedelta(seconds=1))
    r = _dang_ky_gv(client)
    assert "loi=ma_giao_vien_sai" in r.headers["location"]
    assert _user("nam@truong.edu.vn") is None


def test_a_school_with_no_code_at_all_admits_nobody(client):
    _truong(ma_giao_vien=None, ma_het_han=None)
    r = _dang_ky_gv(client, ma_truong="BATKYCAIGI")
    assert "loi=ma_giao_vien_sai" in r.headers["location"]


def test_minting_a_new_code_kills_the_old_one_immediately(client):
    """Đây là cách thu hồi một mã bị lộ trước khi hết ba ngày."""
    db = SessionLocal()
    try:
        truong = db.query(School).first()
        ma_cu = truong.ma_giao_vien
        ma_moi = cap_ma_moi(db, truong)
    finally:
        db.close()

    assert ma_moi != ma_cu
    assert "loi=ma_giao_vien_sai" in _dang_ky_gv(client, ma_truong=ma_cu).headers["location"]
    assert _dang_ky_gv(client, ma_truong=ma_moi).headers["location"] == "/giao-vien"


def test_a_switched_off_school_leaves_the_dropdown_and_its_code_stops_working(client):
    _truong(hoat_dong=False)
    page = client.get("/dang-ky/giao-vien").text
    assert "THPT Nguyễn Trãi" not in page
    assert "loi=ma_giao_vien_sai" in _dang_ky_gv(client).headers["location"]


def test_the_dropdown_lists_partner_schools(client):
    page = client.get("/dang-ky/giao-vien").text
    assert "THPT Nguyễn Trãi" in page
    # Không có ô nhập tên trường tự do — nếu có thì ô chọn chỉ là trang trí.
    assert 'name="truong_id"' in page
    assert "Không thấy trường của bạn" in page


def test_a_teacher_signup_needs_a_school_chosen(client):
    r = _dang_ky_gv(client, truong_id="")
    assert "loi=truong_sai" in r.headers["location"]


def test_the_code_route_is_throttled_so_three_days_is_not_an_afternoon(client):
    for _ in range(throttle.MAX_ATTEMPTS):
        _dang_ky_gv(client, ma_truong=sinh_ma())
    r = _dang_ky_gv(client)  # mã đúng, nhưng đã bị khoá
    assert "loi=thu_lai_sau" in r.headers["location"]


def test_a_suspended_teacher_loses_every_door_to_student_writing(client):
    """Hạn ba ngày chặn việc lập thêm tài khoản, nhưng không thu hồi được tài
    khoản đã lập. Đình chỉ mới là thứ làm việc đó."""
    client.post(
        "/dang-nhap",
        data={"email": SEED_EMAILS["giao_vien"], "mat_khau": SEED_PASSWORD},
        follow_redirects=False,
    )
    db = SessionLocal()
    try:
        lop = db.query(Class).first()
        lop_id = lop.id
        hoc_sinh_id = lop.students[0].id
        gv = db.query(User).filter(User.email == SEED_EMAILS["giao_vien"]).first()
        gv.status = "tam_khoa"
        db.commit()
    finally:
        db.close()

    for url in [
        "/giao-vien",
        f"/giao-vien/lop/{lop_id}",
        f"/giao-vien/hoc-sinh/{hoc_sinh_id}",
        "/giao-vien/tien-do",
    ]:
        r = client.get(url, follow_redirects=False)
        assert r.status_code in (303, 403, 404), f"{url} → {r.status_code}"


def test_can_teach_needs_both_the_role_and_an_active_account():
    assert User(role="teacher", status="hoat_dong").can_teach
    assert not User(role="teacher", status="tam_khoa").can_teach
    assert not User(role="student", status="hoat_dong").can_teach


def test_a_new_class_records_which_school_holds_the_data(client):
    """LEGAL.md đặt nhà trường là bên kiểm soát dữ liệu. Suy ngược từ giáo viên
    thì giáo viên chuyển trường sẽ kéo theo cả lớp cũ."""
    db = SessionLocal()
    try:
        lop = db.query(Class).first()
        assert lop.school_id is not None
        truong_cu = lop.school_id

        gv = db.get(User, lop.teacher_id)
        gv.school_id = None  # giáo viên rời trường
        db.commit()

        db.refresh(lop)
        assert lop.school_id == truong_cu
    finally:
        db.close()


def test_an_expired_code_reads_as_expired():
    het_han = School(ten="X", hoat_dong=True, ma_giao_vien="ABC",
                     ma_het_han=datetime.now() - timedelta(minutes=1))
    con_han = School(ten="Y", hoat_dong=True, ma_giao_vien="ABC",
                     ma_het_han=datetime.now() + timedelta(minutes=1))
    chua_cap = School(ten="Z", hoat_dong=True)
    assert not ma_con_han(het_han)
    assert ma_con_han(con_han)
    assert not ma_con_han(chua_cap)


def test_generated_codes_avoid_letters_that_get_misread():
    """Mã được đọc qua điện thoại và chép tay, nên bỏ I, O, 0, 1."""
    for _ in range(50):
        assert not set(sinh_ma()) & set("IO01")
