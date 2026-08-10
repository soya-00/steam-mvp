from __future__ import annotations

import csv
import io
import json
import zipfile

from tests.conftest import login_student, login_teacher

# Những chuỗi này phải có thật trong dữ liệu gieo sẵn, nếu không phép thử rò rỉ
# bên dưới sẽ luôn xanh mà chẳng kiểm tra gì.
STUDENT_WRITING = "Em nghĩ chưa thể kết luận căng tin là nguyên nhân"
AI_SYNTHESIS = "Điều đáng chú ý nhất ở bạn"
PORTFOLIO_TEXT = "Kế hoạch điều tra đợt bệnh"
STUDENT_NAME = "Nguyễn Khánh Linh"
TEACHER_OWN_WORDS = "Cô rất thích chỗ em nhận ra"


def _zip_text(payload: bytes) -> tuple[zipfile.ZipFile, str]:
    archive = zipfile.ZipFile(io.BytesIO(payload))
    joined = "\n".join(
        archive.read(name).decode("utf-8-sig") for name in archive.namelist()
    )
    return archive, joined


def test_seed_still_contains_the_strings_the_leak_guard_looks_for(client):
    login_teacher(client)
    page = client.get("/giao-vien/hoc-sinh/2").text
    assert STUDENT_WRITING in page or PORTFOLIO_TEXT in page


def test_account_page_opens_for_both_roles(client):
    login_student(client)
    student = client.get("/tai-khoan")
    assert student.status_code == 200
    assert "Quyền riêng tư" in student.text

    login_teacher(client)
    teacher = client.get("/tai-khoan")
    assert teacher.status_code == 200
    # Quyền riêng tư là mục của học sinh, giáo viên không có.
    assert "Bảng đối chiếu mã học sinh" in teacher.text


def test_menu_rows_depend_on_role(client):
    login_student(client)
    page = client.get("/trang-ca-nhan").text
    assert "Quyền riêng tư" in page
    assert "Tải dữ liệu của tôi" in page
    for teacher_only in ["Hướng dẫn cho thầy cô", "Mã lớp của tôi", "Tạo lớp mới"]:
        assert teacher_only not in page, teacher_only

    login_teacher(client)
    page = client.get("/giao-vien").text
    assert "Tải dữ liệu của tôi" in page
    assert "Quyền riêng tư" not in page
    for teacher_only in ["Hướng dẫn cho thầy cô", "Mã lớp của tôi", "Tạo lớp mới",
                         "Danh sách lớp"]:
        assert teacher_only in page, teacher_only


def test_menu_trigger_is_announced_to_assistive_tech(client):
    login_student(client)
    page = client.get("/trang-ca-nhan").text
    assert 'id="nut-tai-khoan"' in page
    for attr in ['aria-haspopup="menu"', 'aria-expanded="false"',
                 'aria-controls="bang-tai-khoan"']:
        assert attr in page, attr


def test_display_name_saves(client):
    login_student(client)
    client.post("/tai-khoan/ten", data={"ten": "Linh Nguyễn"})
    assert "Linh Nguyễn" in client.get("/tai-khoan").text


def test_a_blocked_name_is_refused_and_the_old_one_survives(client):
    login_student(client)
    client.post("/tai-khoan/ten", data={"ten": "Tên Tử Tế"})
    before = client.get("/tai-khoan").text
    assert "Tên Tử Tế" in before

    client.post("/tai-khoan/ten", data={"ten": "địt mẹ"})
    after = client.get("/tai-khoan").text
    assert "Tên Tử Tế" in after
    assert "địt mẹ" not in after


def test_avatar_saves(client):
    login_student(client)
    client.post("/tai-khoan/avatar", data={"avatar_id": "avatar-5"})
    assert "🐬" in client.get("/trang-ca-nhan").text

    # Giá trị lạ bị bỏ qua thay vì ghi bừa vào cơ sở dữ liệu.
    client.post("/tai-khoan/avatar", data={"avatar_id": "avatar-khong-co-that"})
    assert "🐬" in client.get("/trang-ca-nhan").text


def test_student_export_is_json_and_holds_their_own_writing(client):
    login_student(client)
    r = client.get("/tai-khoan/du-lieu")
    assert r.status_code == 200
    assert "attachment" in r.headers["content-disposition"]
    assert r.headers["content-disposition"].endswith('.json"')

    data = json.loads(r.content)
    assert set(data) >= {
        "nguoi_dung", "lop", "nhat_ky", "hanh_trinh", "ho_so",
        "huy_hieu", "loi_nhan_tu_giao_vien",
    }
    # Bài của chính mình thì xuất đủ.
    assert STUDENT_WRITING in r.content.decode()
    # Nhưng không kèm email của ai.
    assert "gals.demo" not in r.content.decode()


def test_teacher_export_is_a_zip_of_three_tables(client):
    login_teacher(client)
    r = client.get("/tai-khoan/du-lieu")
    assert r.status_code == 200
    assert r.headers["content-disposition"].endswith('.zip"')

    archive, _ = _zip_text(r.content)
    assert archive.namelist() == [
        "nhat-ky.csv", "phan-hoi.csv", "nhiem-vu.csv", "HUONG-DAN.txt"
    ]


def test_teacher_export_carries_metadata_not_student_writing(client):
    login_teacher(client)
    archive, joined = _zip_text(client.get("/tai-khoan/du-lieu").content)

    # Phải giải nén rồi mới dò: tìm chuỗi trong byte nén thì lúc nào cũng
    # "sạch", kể cả khi thật sự rò rỉ.
    for label, needle in [
        ("bài học sinh viết", STUDENT_WRITING),
        ("lời tổng kết của AI", AI_SYNTHESIS),
        ("mô tả trong hồ sơ", PORTFOLIO_TEXT),
        ("tên thật học sinh", STUDENT_NAME),
    ]:
        assert needle not in joined, label

    # Nhận xét do chính giáo viên viết thì xuất đủ.
    assert TEACHER_OWN_WORDS in joined
    # Và vẫn có phần thông tin về bài làm.
    assert "Cấp độ đã xong" in joined
    assert "Số câu trả lời" in joined


def test_teacher_csv_opens_correctly_in_a_spreadsheet(client):
    login_teacher(client)
    archive, _ = _zip_text(client.get("/tai-khoan/du-lieu").content)

    for name in ["nhat-ky.csv", "phan-hoi.csv", "nhiem-vu.csv"]:
        raw = archive.read(name)
        # Thiếu BOM là Excel hiện sai toàn bộ dấu tiếng Việt.
        assert raw[:3] == b"\xef\xbb\xbf", name
        rows = list(csv.reader(io.StringIO(raw.decode("utf-8-sig"))))
        assert rows and rows[0], name

    header = list(csv.reader(io.StringIO(archive.read("nhat-ky.csv").decode("utf-8-sig"))))[0]
    assert header[0] == "Mã lớp"
    assert "Mã học sinh" in header


def test_a_name_that_looks_like_a_formula_cannot_run_in_excel(client):
    from app.routers.tai_khoan import _safe_cell

    for danger in ["=SUM(1)", "+1+1", "-2", "@cmd"]:
        assert _safe_cell(danger).startswith("'"), danger
    assert _safe_cell("Nguyễn Khánh Linh") == "Nguyễn Khánh Linh"
    assert _safe_cell(None) == ""


def test_student_codes_are_stable_and_append_only(client):
    from app.db import SessionLocal
    from app.models import Class, ClassMembership, User
    from app.routers.tai_khoan import student_codes

    login_teacher(client)
    with SessionLocal() as db:
        klass = db.query(Class).filter(Class.class_code == "GALS-11A2").first()
        first = student_codes(db, klass)
        assert student_codes(db, klass) == first

        newcomer = User(name="Học Sinh Mới", email="moi@gals.demo", role="student")
        db.add(newcomer)
        db.flush()
        db.add(ClassMembership(student_id=newcomer.id, class_id=klass.id))
        db.commit()

        after = student_codes(db, klass)
        # Thêm người vào cuối không được đánh số lại những em đã có.
        for student_id, code in first.items():
            assert after[student_id] == code
        assert after[newcomer.id] not in first.values()


def test_the_code_to_name_table_never_leaves_the_screen(client):
    login_teacher(client)
    assert STUDENT_NAME in client.get("/tai-khoan").text

    _, joined = _zip_text(client.get("/tai-khoan/du-lieu").content)
    assert STUDENT_NAME not in joined


def test_teacher_menu_pages_are_teacher_only(client):
    login_teacher(client)
    for url in ["/giao-vien/huong-dan", "/giao-vien/ma-lop"]:
        assert client.get(url).status_code == 200, url
    assert "Khi một em viết ra điều đáng lo" in client.get("/giao-vien/huong-dan").text
    assert "GALS-11A2" in client.get("/giao-vien/ma-lop").text

    login_student(client)
    for url in ["/giao-vien/huong-dan", "/giao-vien/ma-lop"]:
        r = client.get(url, follow_redirects=False)
        assert r.status_code == 303, url


def test_display_preferences_have_somewhere_to_apply(client):
    import pathlib

    css = pathlib.Path("static/css/app.css").read_text(encoding="utf-8")
    # Bản rút gọn bỏ dấu nháy trong bộ chọn thuộc tính, nên chấp nhận cả hai kiểu.
    for attr, value in [("data-motion", "giam"), ("data-nen", "phang")]:
        assert (
            f'[{attr}="{value}"]' in css or f"[{attr}={value}]" in css
        ), f"{attr}={value} biến mất khỏi CSS build"

    login_student(client)
    page = client.get("/tai-khoan").text
    for pref in ['data-pref="motion"', 'data-pref="nen"']:
        assert pref in page, pref
    # Cài đặt phải được dán trước khi trang vẽ, nếu không giao diện sẽ nhấp nháy.
    assert "gals-hien-thi" in page
