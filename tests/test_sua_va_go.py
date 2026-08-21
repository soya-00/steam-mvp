"""Tám việc cơ bản mà trước đây không có đường lùi.

Điểm chung của cả tám: một cú bấm nhầm, một chữ gõ sai, hoặc một câu viết vội —
và không có cách nào sửa. Đây là kiểu thiếu sót chỉ lộ ra trong tuần đầu có
người thật dùng, nên nó cần bài kiểm thử hơn là chỗ nào khác.
"""

from __future__ import annotations

import io
import zipfile

from app.db import SessionLocal
from app.models import Assignment, Class, Feedback, JournalEntry, Notification, PortfolioEntry, User
from tests.conftest import login_independent, login_student, login_teacher
from tests.du_lieu_mau import SEED_EMAILS, SEED_PASSWORD


def _lop() -> Class:
    with SessionLocal() as db:
        return db.query(Class).filter(Class.class_code == "GALS-11A2").first()


def _user(email: str) -> User:
    with SessionLocal() as db:
        return db.query(User).filter(User.email == email).first()


# ------------------------------------------------------------- gỡ nhiệm vụ

def _nhiem_vu(class_id: int) -> Assignment:
    with SessionLocal() as db:
        return (
            db.query(Assignment)
            .filter(Assignment.class_id == class_id)
            .order_by(Assignment.id)
            .first()
        )


def test_a_teacher_can_take_back_a_task_they_set_by_mistake(client):
    lop_id = _lop().id
    nv = _nhiem_vu(lop_id)
    login_teacher(client)

    client.post(f"/giao-vien/lop/{lop_id}/nhiem-vu/{nv.id}/go", data={})

    with SessionLocal() as db:
        assert db.get(Assignment, nv.id).da_go
    trang = client.get(f"/giao-vien/lop/{lop_id}").text
    assert "Nhiệm vụ đã gỡ (1)" in trang


def test_a_removed_task_disappears_from_the_students_board(client):
    from app.scenarios import get_scenario

    lop_id = _lop().id
    nv = _nhiem_vu(lop_id)
    tieu_de = get_scenario(nv.scenario_id).title

    login_student(client)
    assert tieu_de in client.get("/trang-ca-nhan").text

    client.get("/dang-xuat")
    login_teacher(client)
    client.post(f"/giao-vien/lop/{lop_id}/nhiem-vu/{nv.id}/go", data={})

    client.get("/dang-xuat")
    login_student(client)
    assert tieu_de not in client.get("/trang-ca-nhan").text


def test_removing_a_task_destroys_nothing(client):
    """Gỡ là để nó biến khỏi màn hình, không phải để xoá lịch sử."""
    lop_id = _lop().id
    nv = _nhiem_vu(lop_id)
    login_teacher(client)
    client.post(f"/giao-vien/lop/{lop_id}/nhiem-vu/{nv.id}/go", data={})

    with SessionLocal() as db:
        assert db.get(Assignment, nv.id) is not None

    goi = client.get("/tai-khoan/du-lieu").content
    with zipfile.ZipFile(io.BytesIO(goi)) as z:
        nhiem_vu_csv = z.read("nhiem-vu.csv").decode("utf-8-sig")
    assert "đã gỡ" in nhiem_vu_csv


def test_a_removed_task_can_be_restored(client):
    lop_id = _lop().id
    nv = _nhiem_vu(lop_id)
    login_teacher(client)
    client.post(f"/giao-vien/lop/{lop_id}/nhiem-vu/{nv.id}/go", data={})
    client.post(f"/giao-vien/lop/{lop_id}/nhiem-vu/{nv.id}/khoi-phuc", data={})

    with SessionLocal() as db:
        assert not db.get(Assignment, nv.id).da_go


def test_a_teacher_cannot_touch_a_task_in_someone_elses_class(client):
    """Số hiệu nhiệm vụ đoán được, nên phải kiểm cả lớp chứ không chỉ nhiệm vụ."""
    with SessionLocal() as db:
        gv = User(name="Thầy Khác", email="khac2@gals.demo", role="teacher")
        db.add(gv)
        db.flush()
        lop = Class(teacher_id=gv.id, class_code="GALS-KH2", roster_prefix="HSQQ11",
                    name="Lớp khác")
        db.add(lop)
        db.flush()
        nv = Assignment(class_id=lop.id, field="Toán", mode="online")
        db.add(nv)
        db.commit()
        lop_id, nv_id = lop.id, nv.id

    login_teacher(client)
    r = client.post(f"/giao-vien/lop/{lop_id}/nhiem-vu/{nv_id}/go", data={},
                    follow_redirects=False)
    assert r.headers["location"] == "/giao-vien"
    with SessionLocal() as db:
        assert not db.get(Assignment, nv_id).da_go


# --------------------------------------------------------- sửa và thu lời nhắn

def _loi_nhan() -> Feedback:
    with SessionLocal() as db:
        return db.query(Feedback).order_by(Feedback.id).first()


def test_a_teacher_can_fix_a_typo_in_a_comment(client):
    note = _loi_nhan()
    login_teacher(client)
    client.post(f"/giao-vien/nhan-xet/{note.id}/sua", data={"noi_dung": "Cô viết lại câu này."})

    with SessionLocal() as db:
        sau = db.get(Feedback, note.id)
        assert sau.content == "Cô viết lại câu này."
        assert sau.updated_at is not None


def test_the_student_is_told_the_comment_was_edited(client):
    """Em có thể đã đọc bản cũ rồi. Im lặng viết lại lời một người lớn đã nói
    với một đứa trẻ mới là điều phải tránh, chứ không phải việc sửa."""
    note = _loi_nhan()
    login_teacher(client)
    client.post(f"/giao-vien/nhan-xet/{note.id}/sua", data={"noi_dung": "Câu đã sửa."})

    client.get("/dang-xuat")
    login_student(client)
    trang = client.get("/ho-so").text
    assert "Câu đã sửa." in trang
    assert "đã sửa" in trang


def test_an_unchanged_comment_is_not_marked_as_edited(client):
    note = _loi_nhan()
    login_teacher(client)
    client.post(f"/giao-vien/nhan-xet/{note.id}/sua", data={"noi_dung": note.content})

    with SessionLocal() as db:
        assert db.get(Feedback, note.id).updated_at is None


def test_a_teacher_can_take_a_comment_back(client):
    note = _loi_nhan()
    login_teacher(client)
    client.post(f"/giao-vien/nhan-xet/{note.id}/xoa", data={})

    with SessionLocal() as db:
        assert db.get(Feedback, note.id) is None


def test_a_teacher_cannot_edit_another_teachers_comment(client):
    with SessionLocal() as db:
        gv = User(name="Thầy Khác", email="khac3@gals.demo", role="teacher")
        db.add(gv)
        db.flush()
        note = Feedback(
            teacher_id=gv.id,
            student_id=_user(SEED_EMAILS["hoc_sinh_co_lop"]).id,
            content="Lời của người khác.",
        )
        db.add(note)
        db.commit()
        note_id = note.id

    login_teacher(client)
    client.post(f"/giao-vien/nhan-xet/{note_id}/sua", data={"noi_dung": "Đổi trộm."})
    client.post(f"/giao-vien/nhan-xet/{note_id}/xoa", data={})

    with SessionLocal() as db:
        van_con = db.get(Feedback, note_id)
        assert van_con is not None
        assert van_con.content == "Lời của người khác."


# ------------------------------------------------------------------ đổi email

MOI = "dia-chi-moi@example.com"


def test_a_typo_in_the_signup_email_is_fixable(client):
    login_student(client)
    client.post(
        "/tai-khoan/email",
        data={"mat_khau": SEED_PASSWORD, "email_moi": MOI},
    )
    client.get("/dang-xuat")
    r = client.post(
        "/dang-nhap",
        data={"email": MOI, "mat_khau": SEED_PASSWORD},
        follow_redirects=False,
    )
    assert "loi=" not in r.headers["location"]


def test_changing_the_email_needs_the_current_password(client):
    """Không có bước này thì ai mượn được máy đang mở sẵn cũng đổi được email
    rồi chiếm hẳn tài khoản qua đường đặt lại mật khẩu."""
    login_student(client)
    r = client.post(
        "/tai-khoan/email",
        data={"mat_khau": "doan-bua", "email_moi": MOI},
        follow_redirects=False,
    )
    assert "loi=mat_khau_cu_sai" in r.headers["location"]
    assert _user(SEED_EMAILS["hoc_sinh_co_lop"]) is not None


def test_you_cannot_take_over_an_address_someone_else_uses(client):
    login_student(client)
    r = client.post(
        "/tai-khoan/email",
        data={"mat_khau": SEED_PASSWORD, "email_moi": SEED_EMAILS["giao_vien"]},
        follow_redirects=False,
    )
    assert "loi=email_trung" in r.headers["location"]


def test_a_malformed_address_is_refused(client):
    login_student(client)
    r = client.post(
        "/tai-khoan/email",
        data={"mat_khau": SEED_PASSWORD, "email_moi": "khong-phai-email"},
        follow_redirects=False,
    )
    assert "loi=email_hong" in r.headers["location"]


def test_the_cli_can_rescue_an_account_that_cannot_log_in():
    from app.quan_tri import main

    assert main(["doi-email", SEED_EMAILS["hoc_sinh_doc_lap"], MOI]) == 0
    assert _user(MOI) is not None


# --------------------------------------------------------- nhập lại mật khẩu

def _dang_ky(client, **kwargs):
    data = {
        "ten": "Bạn Mới",
        "email": "banmoi@example.com",
        "mat_khau": "mat-khau-tot-1",
        "mat_khau_lai": "mat-khau-tot-1",
        "tuoi": "17",
        "dong_y": "1",
    }
    data.update(kwargs)
    return client.post("/dang-ky", data=data, follow_redirects=False)


def test_a_mistyped_password_is_caught_before_the_account_exists(client):
    """Gõ nhầm một chữ ở đây là khoá cửa ngay, và đường cứu hộ lại đi qua chính
    địa chỉ email vừa gõ ở trên — có thể cũng nhầm nốt."""
    r = _dang_ky(client, mat_khau_lai="mat-khau-khac-1")
    assert "loi=mat_khau_lech" in r.headers["location"]
    assert _user("banmoi@example.com") is None


def test_matching_passwords_still_create_the_account(client):
    r = _dang_ky(client)
    assert "loi=" not in r.headers["location"]
    assert _user("banmoi@example.com") is not None


def test_the_signup_form_asks_twice(client):
    assert 'name="mat_khau_lai"' in client.get("/dang-ky").text
    assert 'name="mat_khau_lai"' in client.get("/dang-ky/giao-vien").text


# ------------------------------------------------------------------ trang 500

def test_an_unhandled_error_gets_a_real_page(client_tho):
    """Không có trang này thì lỗi rơi ra thành một dòng chữ trần của Starlette —
    đứng trước cả lớp thì nó trông như cả trang web đã sập."""
    from fastapi.testclient import TestClient

    from app.main import app

    @app.get("/thu-gay-loi")
    def _gay_loi():
        raise RuntimeError("cố ý")

    with TestClient(app, raise_server_exceptions=False) as c:
        r = c.get("/thu-gay-loi")
    assert r.status_code == 500
    assert "lỗi là ở phía chúng mình" in r.text
    # Vết lỗi đi vào log máy chủ, không ra màn hình.
    assert "RuntimeError" not in r.text
    assert "Traceback" not in r.text


# ------------------------------------------- học sinh tự bỏ và rút bài của mình

def test_a_student_can_tidy_their_portfolio_without_losing_the_writing(client):
    uid = _user(SEED_EMAILS["hoc_sinh_co_lop"]).id
    with SessionLocal() as db:
        item = db.query(PortfolioEntry).filter(PortfolioEntry.student_id == uid).first()
        item_id, je_id = item.id, item.journal_entry_id
        so_bai = db.query(JournalEntry).filter(JournalEntry.student_id == uid).count()

    login_student(client)
    client.post(f"/ho-so/{item_id}/xoa", data={})

    with SessionLocal() as db:
        assert db.get(PortfolioEntry, item_id) is None
        # Bài viết và cả đoạn hội thoại vẫn nguyên.
        assert db.get(JournalEntry, je_id) is not None
        assert db.query(JournalEntry).filter(JournalEntry.student_id == uid).count() == so_bai


def test_a_student_cannot_remove_someone_elses_portfolio_item(client):
    with SessionLocal() as db:
        khac = db.query(PortfolioEntry).join(User).filter(
            User.email != SEED_EMAILS["hoc_sinh_doc_lap"]
        ).first()
        item_id = khac.id

    login_independent(client)
    client.post(f"/ho-so/{item_id}/xoa", data={})
    with SessionLocal() as db:
        assert db.get(PortfolioEntry, item_id) is not None


def test_a_student_can_withdraw_a_submission(client):
    """Nộp là mở bài của mình cho thầy cô đọc, nên nó phải có đường lùi."""
    uid = _user(SEED_EMAILS["hoc_sinh_co_lop"]).id
    with SessionLocal() as db:
        entry = (
            db.query(JournalEntry)
            .filter(JournalEntry.student_id == uid, JournalEntry.submitted.is_(True))
            .first()
        )
        scenario_id, entry_id = entry.scenario_id, entry.id

    login_student(client)
    client.post(f"/du-an/{scenario_id}/rut", data={})

    with SessionLocal() as db:
        assert not db.get(JournalEntry, entry_id).submitted


def test_a_withdrawn_submission_leaves_the_teachers_view(client, client_tho):
    uid = _user(SEED_EMAILS["hoc_sinh_co_lop"]).id
    with SessionLocal() as db:
        entry = (
            db.query(JournalEntry)
            .filter(JournalEntry.student_id == uid, JournalEntry.submitted.is_(True))
            .first()
        )
        scenario_id = entry.scenario_id
        doan_van = entry.content[:30]

    login_student(client)
    client.post(f"/du-an/{scenario_id}/rut", data={})

    client_tho.get("/")
    ve = client_tho.cookies.get("gals_csrf")
    client_tho.post("/dang-nhap", data={"_csrf": ve, "email": SEED_EMAILS["giao_vien"],
                                        "mat_khau": SEED_PASSWORD}, follow_redirects=False)
    assert doan_van not in client_tho.get(f"/giao-vien/hoc-sinh/{uid}").text


# ------------------------------------------------------------ thu lại thông báo

def test_a_teacher_can_take_back_a_notification(client):
    lop_id = _lop().id
    with SessionLocal() as db:
        tb = Notification(class_id=lop_id, type="workshop", title="Gửi nhầm rồi")
        db.add(tb)
        db.commit()
        tb_id = tb.id

    login_teacher(client)
    assert "Gửi nhầm rồi" in client.get("/giao-vien/thong-bao").text
    client.post(f"/giao-vien/thong-bao/{tb_id}/xoa", data={})

    with SessionLocal() as db:
        assert db.get(Notification, tb_id) is None


def test_a_teacher_cannot_delete_a_platform_wide_notice(client):
    """Thông báo toàn hệ thống là của người vận hành, không phải của giáo viên."""
    with SessionLocal() as db:
        tb = Notification(type="workshop", title="Thông báo chung")
        db.add(tb)
        db.commit()
        tb_id = tb.id

    login_teacher(client)
    client.post(f"/giao-vien/thong-bao/{tb_id}/xoa", data={})
    with SessionLocal() as db:
        assert db.get(Notification, tb_id) is not None


# --------------------------------------------------------------- thẻ học tiếp

def test_the_resume_card_points_at_the_thing_last_worked_on(client):
    """Sắp theo lúc mở thì một em hôm qua mở A, hôm nay làm tiếp B, sẽ được chỉ
    về A — đúng chỗ em không đang làm."""
    from datetime import datetime, timedelta

    from app.models import GuidedSession

    uid = _user(SEED_EMAILS["hoc_sinh_co_lop"]).id
    with SessionLocal() as db:
        cu = (
            db.query(GuidedSession)
            .filter(GuidedSession.student_id == uid, GuidedSession.finished.is_(False))
            .first()
        )
        assert cu is not None
        # Một tình huống mở sau, nhưng đụng tới lâu rồi.
        moi_mo = GuidedSession(
            student_id=uid,
            scenario_id="cong-cu-nao-that-su-giup",
            created_at=datetime.now(),
            updated_at=datetime.now() - timedelta(days=5),
        )
        db.add(moi_mo)
        # Còn cái cũ thì vừa viết xong.
        cu.updated_at = datetime.now()
        db.commit()
        dang_lam = cu.scenario_id

    login_student(client)
    trang = client.get("/trang-ca-nhan").text
    from app.scenarios import get_scenario

    assert get_scenario(dang_lam).title in trang


def test_last_activity_moves_when_a_student_writes_again():
    """Cột "hoạt động lần cuối" từng đọc `created_at`, tức là nó báo hoạt động
    *đầu tiên* — sai âm thầm, và càng để lâu càng sai."""
    from datetime import datetime, timedelta

    from app.models import GuidedSession
    from app.progress import last_activity

    gs = GuidedSession(
        student_id=1,
        scenario_id="x",
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 6, 1),
    )
    assert last_activity(gs) == datetime(2026, 6, 1)
    assert last_activity(None) is None
    # Hàng cũ chưa có updated_at thì rơi về created_at chứ không nổ.
    cu = GuidedSession(student_id=1, scenario_id="x", created_at=datetime(2026, 1, 1))
    cu.updated_at = None
    assert last_activity(cu) == datetime(2026, 1, 1)
    assert timedelta(0) == timedelta(0)
