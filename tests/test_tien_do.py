from __future__ import annotations

import re

from app.scenarios import all_scenarios
from tests.conftest import login_student, login_teacher

LEVEL_1 = "/giao-vien/tien-do"


def test_all_three_levels_open_for_a_teacher(client):
    login_teacher(client)
    assert client.get(LEVEL_1).status_code == 200

    field = client.get(f"{LEVEL_1}/toan")
    assert field.status_code == 200
    assert "Chia 900 triệu" in field.text

    scenario = client.get(f"{LEVEL_1}/toan/phan-bo-quy-hoc-bong")
    assert scenario.status_code == 200
    assert "Nguyễn Khánh Linh" in scenario.text


def test_progress_pages_are_teacher_only(client):
    login_student(client)
    for url in [LEVEL_1, f"{LEVEL_1}/toan", f"{LEVEL_1}/toan/phan-bo-quy-hoc-bong"]:
        r = client.get(url, follow_redirects=False)
        assert r.status_code == 303, url


def test_unknown_field_or_mismatched_scenario_falls_back(client):
    login_teacher(client)
    assert client.get(f"{LEVEL_1}/khong-co-that", follow_redirects=False).status_code == 303
    # Tình huống Toán không nằm dưới nhánh Khoa học.
    mismatched = client.get(f"{LEVEL_1}/khoa_hoc/phan-bo-quy-hoc-bong", follow_redirects=False)
    assert mismatched.status_code == 303


def test_counts_match_the_seeded_data(client):
    login_teacher(client)
    page = client.get(f"{LEVEL_1}/toan/phan-bo-quy-hoc-bong").text

    # Linh đang dở tình huống Toán; ba bạn còn lại chưa mở.
    assert re.search(r">\s*1\s*</strong>\s*đang làm", page)
    assert re.search(r">\s*0\s*</strong>\s*đã xong", page)

    done = client.get(f"{LEVEL_1}/khoa_hoc/dich-te-truong-noi-tru").text
    assert re.search(r">\s*1\s*</strong>\s*đã xong", done)


def test_independent_work_is_not_hidden(client):
    login_teacher(client)
    page = client.get(f"{LEVEL_1}/toan").text
    # Không ai giao tình huống Toán, nhưng Linh đang làm nên nó vẫn phải hiện.
    assert "Đang làm mà chưa được giao" in page
    assert "Chia 900 triệu" in page


def test_a_whole_field_assignment_fans_out(client):
    from app.db import SessionLocal
    from app.models import Assignment, Class

    login_teacher(client)
    with SessionLocal() as db:
        klass = db.query(Class).filter(Class.class_code == "GALS-11A2").first()
        db.add(Assignment(class_id=klass.id, field="Toán", mode="online", note="Cả nhánh"))
        db.commit()

    page = client.get(f"{LEVEL_1}/toan").text
    assert "cả nhánh" in page
    for scenario in all_scenarios():
        if scenario.field == "Toán":
            assert scenario.title in page


def test_class_filter_narrows_the_list(client):
    login_teacher(client)
    from app.db import SessionLocal
    from app.models import Class

    with SessionLocal() as db:
        only = db.query(Class).filter(Class.class_code == "GALS-10B1").first()
        class_id = only.id

    page = client.get(f"{LEVEL_1}/toan/phan-bo-quy-hoc-bong?lop={class_id}").text
    assert "Đỗ Hải Yến" in page
    assert "Nguyễn Khánh Linh" not in page


def test_stage_state_is_spoken_not_only_colour(client):
    login_teacher(client)
    page = client.get(f"{LEVEL_1}/toan/phan-bo-quy-hoc-bong").text
    assert 'role="img"' in page
    assert "cấp độ đã xong" in page


def test_the_teacher_view_and_the_student_view_agree(client):
    from app.db import SessionLocal
    from app.models import GuidedSession
    from app.progress import stage_states
    from app.routers.student import _progress
    from app.scenarios import get_scenario

    scenario = get_scenario("phan-bo-quy-hoc-bong")
    with SessionLocal() as db:
        gs = db.query(GuidedSession).filter(
            GuidedSession.scenario_id == scenario.id
        ).first()
        assert gs is not None
        assert _progress(scenario, gs) == stage_states(scenario, gs)


def test_pages_do_not_query_once_per_student(client):
    """Chặn kiểu N+1: số câu truy vấn phải theo số lớp, không theo số học sinh."""
    import json

    from sqlalchemy import event

    from app.db import SessionLocal, engine
    from app.models import Class, ClassMembership, GuidedSession, User

    login_teacher(client)
    with SessionLocal() as db:
        teacher = db.query(User).filter(User.email == "co.mai@gals.demo").first()
        klass = Class(teacher_id=teacher.id, class_code="GALS-BIG",
                      roster_prefix="HSBIG9", name="Lớp đông")
        db.add(klass)
        db.flush()
        for i in range(60):
            student = User(name=f"HS {i:02d}", email=f"big{i}@gals.demo", role="student")
            db.add(student)
            db.flush()
            db.add(ClassMembership(student_id=student.id, class_id=klass.id))
            db.add(
                GuidedSession(
                    student_id=student.id,
                    scenario_id="dich-te-truong-noi-tru",
                    stage_index=1,
                    transcript=json.dumps(
                        [{"kind": "question", "stage": "s", "label": "l",
                          "text": "q", "answer": "a"}]
                    ),
                )
            )
        db.commit()
        class_id = klass.id

    counter = {"n": 0}

    def bump(*args, **kwargs):
        counter["n"] += 1

    event.listen(engine, "before_cursor_execute", bump)
    try:
        for url, ceiling in [
            ("/giao-vien/tien-do", 40),
            ("/giao-vien/tien-do/khoa_hoc/dich-te-truong-noi-tru", 40),
            ("/tai-khoan/du-lieu", 60),
            # Trang lớp từng chạy hai câu truy vấn cho mỗi em, cộng một câu nữa
            # để nạp chính em đó — khoảng 3N.
            (f"/giao-vien/lop/{class_id}", 40),
        ]:
            counter["n"] = 0
            assert client.get(url).status_code == 200, url
            assert counter["n"] < ceiling, f"{url}: {counter['n']} câu truy vấn cho 60 học sinh"
    finally:
        event.remove(engine, "before_cursor_execute", bump)
