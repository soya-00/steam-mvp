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


# ------------------------------------------------ giáo viên tự quản lý được lớp

def _lop_khac() -> Class:
    """Lớp của một giáo viên khác — dựng riêng để thử chuyện chéo lớp."""
    db = SessionLocal()
    try:
        gv = User(name="Thầy Khác", email="khac@gals.demo", role="teacher",
                  status="hoat_dong")
        db.add(gv)
        db.flush()
        lop = Class(teacher_id=gv.id, class_code="GALS-KHAC", roster_prefix="HSZZ99",
                    name="Lớp của người khác")
        db.add(lop)
        db.commit()
        db.refresh(lop)
        return lop
    finally:
        db.close()


def test_a_teacher_can_remove_a_student_who_joined_the_wrong_class(client):
    lop_id = _lop().id
    uid = _user(SEED_EMAILS["hoc_sinh_co_lop"]).id
    assert _o_trong_lop(SEED_EMAILS["hoc_sinh_co_lop"], lop_id)

    login_teacher(client)
    client.post(f"/giao-vien/lop/{lop_id}/go/{uid}", data={})

    assert not _o_trong_lop(SEED_EMAILS["hoc_sinh_co_lop"], lop_id)
    assert "Nguyễn Khánh Linh" not in client.get(f"/giao-vien/lop/{lop_id}").text


def test_the_remove_confirmation_says_the_student_can_come_back(client):
    """Gỡ không phải là chặn. Thầy cô bấm nút này thường tưởng mình vừa đóng
    một cánh cửa, nên chỗ xác nhận phải nói thẳng và chỉ sang chỗ đổi mã."""
    login_teacher(client)
    page = client.get(f"/giao-vien/lop/{_lop().id}").text
    assert "mã lớp vẫn nhận em ấy" in page
    assert 'href="#quan-ly"' in page


def test_a_removed_student_really_can_rejoin_with_the_same_code(client):
    """Nếu bài này hỏng thì lời nhắn ở trên thành lời nói dối."""
    lop_id = _lop().id
    uid = _user(SEED_EMAILS["hoc_sinh_co_lop"]).id

    login_teacher(client)
    client.post(f"/giao-vien/lop/{lop_id}/go/{uid}", data={})
    assert not _o_trong_lop(SEED_EMAILS["hoc_sinh_co_lop"], lop_id)

    client.get("/dang-xuat")
    login_student(client)
    client.post("/tai-khoan/vao-lop", data={"ma": "GALS-11A2"})
    assert _o_trong_lop(SEED_EMAILS["hoc_sinh_co_lop"], lop_id)


def test_rotating_the_code_is_what_actually_keeps_a_removed_student_out(client):
    lop_id = _lop().id
    uid = _user(SEED_EMAILS["hoc_sinh_co_lop"]).id

    login_teacher(client)
    client.post(f"/giao-vien/lop/{lop_id}/go/{uid}", data={})
    client.post(f"/giao-vien/lop/{lop_id}/doi-ma", data={})

    client.get("/dang-xuat")
    login_student(client)
    r = client.post("/tai-khoan/vao-lop", data={"ma": "GALS-11A2"}, follow_redirects=False)
    assert "loi=ma_lop_sai" in r.headers["location"]
    assert not _o_trong_lop(SEED_EMAILS["hoc_sinh_co_lop"], lop_id)


def test_removing_a_student_keeps_everything_the_student_wrote(client):
    from app.models import JournalEntry

    lop_id = _lop().id
    uid = _user(SEED_EMAILS["hoc_sinh_co_lop"]).id

    db = SessionLocal()
    try:
        truoc = db.query(JournalEntry).filter(JournalEntry.student_id == uid).count()
    finally:
        db.close()

    login_teacher(client)
    client.post(f"/giao-vien/lop/{lop_id}/go/{uid}", data={})

    db = SessionLocal()
    try:
        assert db.query(JournalEntry).filter(JournalEntry.student_id == uid).count() == truoc
        assert truoc > 0
        assert db.get(User, uid) is not None
    finally:
        db.close()


def test_a_teacher_cannot_remove_a_student_from_someone_elses_class(client):
    lop_khac = _lop_khac()
    uid = _user(SEED_EMAILS["hoc_sinh_co_lop"]).id
    db = SessionLocal()
    try:
        db.add(ClassMembership(student_id=uid, class_id=lop_khac.id))
        db.commit()
    finally:
        db.close()

    login_teacher(client)
    r = client.post(f"/giao-vien/lop/{lop_khac.id}/go/{uid}", data={},
                    follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/giao-vien"
    assert _o_trong_lop(SEED_EMAILS["hoc_sinh_co_lop"], lop_khac.id)


def test_rotating_the_code_kills_the_old_one_and_keeps_the_roster(client):
    """Mã bị chụp màn hình là lý do có nút này."""
    lop_id = _lop().id
    login_teacher(client)
    client.post(f"/giao-vien/lop/{lop_id}/doi-ma", data={})

    db = SessionLocal()
    try:
        lop = db.get(Class, lop_id)
        assert lop.class_code != "GALS-11A2"
        assert lop.class_code.startswith("GALS-")
        # Đổi mã không đuổi ai ra khỏi lớp.
        assert db.query(ClassMembership).filter(
            ClassMembership.class_id == lop_id
        ).count() > 0
    finally:
        db.close()

    # Mã cũ không vào được nữa.
    client.get("/dang-xuat")
    login_independent(client)
    r = client.post("/tai-khoan/vao-lop", data={"ma": "GALS-11A2"}, follow_redirects=False)
    assert "loi=ma_lop_sai" in r.headers["location"]


def test_rotating_the_code_does_not_rename_anyone_in_the_export(client):
    """HUONG-DAN.txt hứa cùng một em thì lần xuất nào cũng ra cùng một mã ẩn
    danh. Nếu mã ẩn danh bám theo mã lớp thì đổi mã một lần là đổi tên toàn bộ
    học sinh so với bản thầy cô đã tải tuần trước."""
    from app.routers.tai_khoan import student_codes

    lop_id = _lop().id
    db = SessionLocal()
    try:
        truoc = student_codes(db, db.get(Class, lop_id))
    finally:
        db.close()

    login_teacher(client)
    client.post(f"/giao-vien/lop/{lop_id}/doi-ma", data={})

    db = SessionLocal()
    try:
        sau = student_codes(db, db.get(Class, lop_id))
    finally:
        db.close()
    assert sau == truoc and truoc


def test_a_teacher_cannot_rotate_someone_elses_code(client):
    lop_khac = _lop_khac()
    login_teacher(client)
    r = client.post(f"/giao-vien/lop/{lop_khac.id}/doi-ma", data={},
                    follow_redirects=False)
    assert r.headers["location"] == "/giao-vien"

    db = SessionLocal()
    try:
        assert db.get(Class, lop_khac.id).class_code == "GALS-KHAC"
    finally:
        db.close()


def test_a_teacher_can_rename_a_class(client):
    lop_id = _lop().id
    login_teacher(client)
    client.post(f"/giao-vien/lop/{lop_id}/sua", data={"ten_lop": "11A2 — học kỳ hai"})

    db = SessionLocal()
    try:
        assert db.get(Class, lop_id).name == "11A2 — học kỳ hai"
    finally:
        db.close()


def test_a_class_name_goes_through_the_same_filter_as_a_persons_name(client):
    """Tên lớp hiện trên màn hình học sinh, nên không thể là chỗ trống."""
    lop_id = _lop().id
    login_teacher(client)
    r = client.post(f"/giao-vien/lop/{lop_id}/sua", data={"ten_lop": "   "},
                    follow_redirects=False)
    assert "loi=ten_trong" in r.headers["location"]

    db = SessionLocal()
    try:
        assert db.get(Class, lop_id).name == "11A2 — Chuyên đề STEAM"
    finally:
        db.close()


def test_closing_a_class_stops_the_code_but_keeps_the_work_readable(client):
    lop_id = _lop().id
    login_teacher(client)
    client.post(f"/giao-vien/lop/{lop_id}/dong", data={})

    # Vẫn mở đọc được, và nói rõ là đã kết thúc.
    trang = client.get(f"/giao-vien/lop/{lop_id}")
    assert trang.status_code == 200
    assert "Đã kết thúc" in trang.text
    assert "Nguyễn Khánh Linh" in trang.text

    # Nhưng rời khỏi danh sách lớp đang dạy, và nằm sau một lần bấm.
    nha = client.get("/giao-vien").text
    assert "Lớp đã kết thúc (1)" in nha

    # Và mã không nhận thêm ai.
    client.get("/dang-xuat")
    login_independent(client)
    r = client.post("/tai-khoan/vao-lop", data={"ma": "GALS-11A2"}, follow_redirects=False)
    assert "loi=ma_lop_sai" in r.headers["location"]


def test_a_closed_class_takes_no_new_assignments(client):
    from app.models import Assignment

    lop_id = _lop().id
    login_teacher(client)
    client.post(f"/giao-vien/lop/{lop_id}/dong", data={})

    db = SessionLocal()
    try:
        truoc = db.query(Assignment).filter(Assignment.class_id == lop_id).count()
    finally:
        db.close()

    r = client.post(
        f"/giao-vien/lop/{lop_id}/giao",
        data={"muc_tieu": "linh-vuc:khoa_hoc", "hinh_thuc": "online"},
        follow_redirects=False,
    )
    assert "loi=lop_da_dong" in r.headers["location"]

    db = SessionLocal()
    try:
        assert db.query(Assignment).filter(Assignment.class_id == lop_id).count() == truoc
    finally:
        db.close()


def test_a_closed_class_drops_out_of_the_code_sheet_and_the_context_picker(client):
    lop_id = _lop().id
    login_teacher(client)
    client.post(f"/giao-vien/lop/{lop_id}/dong", data={})

    assert "GALS-11A2" not in client.get("/giao-vien/ma-lop").text
    assert "11A2 — Chuyên đề STEAM" not in client.get("/chon-khong-gian").text


def test_reopening_a_class_puts_it_back(client):
    lop_id = _lop().id
    login_teacher(client)
    client.post(f"/giao-vien/lop/{lop_id}/dong", data={})
    client.post(f"/giao-vien/lop/{lop_id}/mo-lai", data={})

    assert "Lớp đã kết thúc" not in client.get("/giao-vien").text

    client.get("/dang-xuat")
    login_independent(client)
    client.post("/tai-khoan/vao-lop", data={"ma": "GALS-11A2"})
    assert _o_trong_lop(SEED_EMAILS["hoc_sinh_doc_lap"], lop_id)


def test_a_teacher_cannot_close_someone_elses_class(client):
    lop_khac = _lop_khac()
    login_teacher(client)
    r = client.post(f"/giao-vien/lop/{lop_khac.id}/dong", data={}, follow_redirects=False)
    assert r.headers["location"] == "/giao-vien"

    db = SessionLocal()
    try:
        assert not db.get(Class, lop_khac.id).da_dong
    finally:
        db.close()


def test_a_new_class_gets_an_export_prefix_unrelated_to_its_code(client):
    """Hai định danh, hai yêu cầu ngược nhau: mã lớp phải đổi được, mã ẩn danh
    phải đứng yên. Buộc vào nhau thì một trong hai chắc chắn thua."""
    login_teacher(client)
    client.post("/giao-vien/lop/tao", data={"ten_lop": "12C1 — thử nghiệm"})

    db = SessionLocal()
    try:
        lop = db.query(Class).filter(Class.name == "12C1 — thử nghiệm").first()
        assert lop is not None
        assert lop.roster_prefix
        assert lop.roster_prefix != lop.class_code
        assert lop.class_code not in lop.roster_prefix
        assert lop.roster_prefix not in lop.class_code
        # Nhà trường là bên kiểm soát dữ liệu, nên lớp phải nhớ trường của mình.
        assert lop.school_id is not None
    finally:
        db.close()


def test_no_class_anywhere_derives_its_export_prefix_from_its_code():
    """Mã lớp luôn bắt đầu bằng "GALS-", tiền tố hồ sơ luôn bắt đầu bằng "HS",
    nên hai không gian tên này không thể chạm nhau."""
    db = SessionLocal()
    try:
        for lop in db.query(Class).all():
            assert lop.roster_prefix.startswith("HS"), lop.roster_prefix
            assert not lop.roster_prefix.startswith("GALS-")
            assert lop.class_code not in lop.roster_prefix
    finally:
        db.close()


def test_export_codes_carry_no_trace_of_the_class_code(client):
    from app.routers.tai_khoan import student_codes

    db = SessionLocal()
    try:
        lop = db.get(Class, _lop().id)
        for ma in student_codes(db, lop).values():
            assert lop.class_code not in ma
            assert ma.startswith("HS")
    finally:
        db.close()


def test_the_download_names_the_class_and_never_carries_the_live_code(client):
    """Mã lớp là thứ đổi được khi bị lộ, mà một tệp đã tải về thì không thu lại
    được. Nên bản tải về gọi lớp bằng tên, không bằng mã."""
    import io
    import zipfile

    login_teacher(client)
    goi = client.get("/tai-khoan/du-lieu").content
    with zipfile.ZipFile(io.BytesIO(goi)) as z:
        chu = "\n".join(z.read(n).decode("utf-8-sig") for n in z.namelist())

    assert "11A2 — Chuyên đề STEAM" in chu
    db = SessionLocal()
    try:
        for lop in db.query(Class).all():
            assert lop.class_code not in chu, lop.class_code
    finally:
        db.close()


def test_the_class_page_offers_the_controls_it_describes(client):
    login_teacher(client)
    page = client.get(f"/giao-vien/lop/{_lop().id}").text
    assert "/doi-ma" in page
    assert "/dong" in page
    assert "/sua" in page
    assert "/go/" in page
    # Không có nút xoá lớp: trong đợt thử nghiệm không nên có nút nào huỷ được
    # dữ liệu thật.
    assert "/xoa" not in page


# ------------------------------------------- giáo viên cũng đổi được mật khẩu

def test_a_teacher_can_change_their_own_password(client):
    """Điều khoản 2.4 bảo mọi người đổi mật khẩu khi nghi bị lộ, không chỉ học
    sinh. Trang tài khoản từng giấu hẳn mục này khỏi giáo viên."""
    login_teacher(client)
    page = client.get("/tai-khoan").text
    assert "/tai-khoan/mat-khau" in page

    client.post(
        "/tai-khoan/mat-khau",
        data={"mat_khau_cu": SEED_PASSWORD, "mat_khau_moi": MOI},
    )
    client.get("/dang-xuat")
    r = client.post(
        "/dang-nhap",
        data={"email": SEED_EMAILS["giao_vien"], "mat_khau": MOI},
        follow_redirects=False,
    )
    assert "loi=" not in r.headers["location"]


def test_the_account_page_never_shows_a_raw_error_code(client):
    login_student(client)
    page = client.get("/tai-khoan?loi=mat_khau_cu_sai").text
    assert "mat_khau_cu_sai" not in page
    assert "Mật khẩu hiện tại chưa đúng." in page


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
