from __future__ import annotations

import re

from app.db import SessionLocal
from app.models import Feedback, User
from tests.conftest import login_independent, login_student, login_teacher

MARK = "ZZQ-KIEM-THU-RIENG-TU-4517"


def _independent_id() -> int:
    db = SessionLocal()
    try:
        return db.query(User).filter(User.email == "trang@gals.demo").first().id
    finally:
        db.close()


def test_teacher_cannot_read_independent_student(client):
    login_teacher(client)
    r = client.get(f"/giao-vien/hoc-sinh/{_independent_id()}", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/giao-vien"


def test_teacher_cannot_write_feedback_to_independent_student(client):
    login_teacher(client)
    sid = _independent_id()
    client.post(f"/giao-vien/hoc-sinh/{sid}/nhan-xet",
                data={"noi_dung": MARK, "journal_entry_id": ""})
    db = SessionLocal()
    try:
        assert db.query(Feedback).filter(Feedback.content == MARK).count() == 0
        assert db.query(Feedback).filter(Feedback.student_id == sid).count() == 0
    finally:
        db.close()


def test_garbage_share_token_is_404(client):
    assert client.get("/p/khong-phai-token").status_code == 404


def test_public_portfolio_shows_only_shared_items(client):
    login_student(client)
    page = client.get("/ho-so/chia-se").text
    token = re.search(r"/p/([\w\.\-]+)", page).group(1)

    public = client.get(f"/p/{token}").text
    assert "Kế hoạch điều tra" in public

    item_id = re.search(r'id="muc-(\d+)"', client.get("/ho-so").text).group(1)
    client.post(f"/ho-so/{item_id}/chia-se", headers={"HX-Request": "true"})

    public_after = client.get(f"/p/{token}").text
    assert "Kế hoạch điều tra" not in public_after
    assert client.get(f"/p/{token}").status_code == 200
