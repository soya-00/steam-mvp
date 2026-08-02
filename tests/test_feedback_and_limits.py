from __future__ import annotations

import pytest

from app import metrics
from app.db import SessionLocal
from app.media import validate_url
from app.models import JournalEntry, Report
from app.routers import phan_hoi
from app.scenarios import all_scenarios
from tests.conftest import login_independent

DANGEROUS = [
    "javascript:alert(1)",
    "JavaScript:alert(document.cookie)",
    "data:text/html,<script>alert(1)</script>",
    "vbscript:msgbox(1)",
    "file:///etc/passwd",
    "https://user:pass@example.com/a.png",
    "https://" + "a" * 600,
]

SAFE = [
    "",
    "https://images.example.com/anh.jpg",
    "http://vidu.vn/hinh.png",
]


@pytest.mark.parametrize("url", DANGEROUS)
def test_dangerous_urls_are_rejected(url):
    cleaned, error = validate_url(url)
    assert cleaned == ""
    assert error


@pytest.mark.parametrize("url", SAFE)
def test_ordinary_urls_pass(url):
    cleaned, error = validate_url(url)
    assert error is None
    assert cleaned == url.strip()


def test_submitting_a_javascript_url_never_reaches_the_database(client):
    login_independent(client)
    sid = all_scenarios()[0].id
    r = client.post(
        f"/du-an/{sid}/nop",
        data={"mo_ta": "Xong rồi ạ", "anh": "javascript:alert(1)", "video": ""},
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert "loi=" in r.headers.get("location", "")

    db = SessionLocal()
    try:
        stored = [e.image_url or "" for e in db.query(JournalEntry).all()]
    finally:
        db.close()
    assert all("javascript" not in url.lower() for url in stored)


def _reset_reports():
    phan_hoi._sent.clear()
    db = SessionLocal()
    try:
        db.query(Report).delete()
        db.commit()
    finally:
        db.close()


def test_report_is_stored_without_identifying_the_student(client):
    _reset_reports()
    login_independent(client)
    r = client.post(
        "/phan-hoi/bao-cao",
        data={"ly_do": "khong_phu_hop", "trich_dan": "Câu trả lời bị báo cáo", "ghi_chu": "Câu này lạc đề ạ"},
    )
    assert r.status_code == 200
    assert "Cảm ơn" in r.text

    db = SessionLocal()
    try:
        rows = db.query(Report).all()
        assert len(rows) == 1
        row = rows[0]
        assert row.kind == "tra_loi_ai"
        assert row.reason == "khong_phu_hop"
        assert row.reported_text == "Câu trả lời bị báo cáo"
        assert not hasattr(row, "student_id")
    finally:
        db.close()


def test_report_note_goes_through_the_input_filter(client):
    _reset_reports()
    login_independent(client)
    r = client.post("/phan-hoi/bao-cao", data={"ly_do": "khac", "ghi_chu": "vcl chán vl"})
    assert "chưa gửi được" in r.text

    db = SessionLocal()
    try:
        assert db.query(Report).count() == 0
    finally:
        db.close()


def test_reports_are_rate_limited(client):
    _reset_reports()
    login_independent(client)
    for _ in range(phan_hoi.MAX_PER_SESSION):
        assert "Cảm ơn" in client.post("/phan-hoi/bao-cao", data={"ly_do": "khac"}).text
    blocked = client.post("/phan-hoi/bao-cao", data={"ly_do": "khac"})
    assert "khá nhiều báo cáo" in blocked.text
    _reset_reports()


def test_feedback_rejects_empty_and_stores_real_text(client):
    _reset_reports()
    login_independent(client)
    assert "chưa viết gì" in client.post("/phan-hoi/gop-y", data={"noi_dung": "   "}).text

    ok = client.post("/phan-hoi/gop-y", data={"noi_dung": "Chỗ chọn lĩnh vực hơi khó bấm trên điện thoại ạ"})
    assert "Cảm ơn" in ok.text

    db = SessionLocal()
    try:
        rows = db.query(Report).filter(Report.kind == "gop_y").all()
        assert len(rows) == 1
        assert "khó bấm" in rows[0].note
    finally:
        db.close()
    _reset_reports()


def test_counters_count_but_never_store_content():
    metrics.reset()
    from app.moderation import screen

    screen("em muon chet qua")
    screen("vcl chán vl")
    screen("em nghĩ là do tải điện")

    snap = metrics.snapshot()
    assert snap.get("screen.crisis") == 1
    assert snap.get("screen.profanity") == 1
    assert "screen.ok" not in snap

    joined = " ".join(snap.keys())
    assert "muon" not in joined and "vcl" not in joined
    assert all(isinstance(v, int) for v in snap.values())
    metrics.reset()


def test_hourly_budget_falls_back_to_offline_instead_of_erroring():
    from app import gemini

    gemini._calls.clear()
    assert gemini.budget_left() == gemini.MAX_CALLS_PER_HOUR
    for _ in range(gemini.MAX_CALLS_PER_HOUR):
        assert gemini._take_from_budget()
    assert not gemini._take_from_budget()
    assert gemini.budget_left() == 0
    gemini._calls.clear()


def test_feedback_content_reaches_the_log_so_someone_can_read_it(client, caplog):
    _reset_reports()
    login_independent(client)
    with caplog.at_level("INFO", logger="gals.phanhoi"):
        client.post("/phan-hoi/gop-y", data={"noi_dung": "Nút chọn lĩnh vực\nhơi khó bấm"})
    written = " ".join(r.getMessage() for r in caplog.records)
    assert "hơi khó bấm" in written
    assert "\n" not in written
    _reset_reports()


def test_confirmation_does_not_promise_the_note_will_survive(client):
    _reset_reports()
    login_independent(client)
    for url, payload in [
        ("/phan-hoi/bao-cao", {"ly_do": "khac"}),
        ("/phan-hoi/gop-y", {"noi_dung": "Góp ý thử cho bản mẫu"}),
    ]:
        body = client.post(url, data=payload).text
        assert "bản mẫu" in body
        assert "khởi động lại" in body
    _reset_reports()


def test_feedback_form_warns_against_personal_details(client):
    login_independent(client)
    page = client.get("/trang-ca-nhan").text
    assert "không gửi đi đâu khác" in page
    assert "Đừng viết thông tin cá nhân" in page


def test_feedback_box_is_reachable_from_both_dashboards(client):
    from tests.conftest import login_teacher

    login_independent(client)
    hub = client.get("/trang-ca-nhan").text
    assert "Góp ý cho GALS" in hub
    assert 'hx-post="/phan-hoi/gop-y"' in hub

    login_teacher(client)
    board = client.get("/giao-vien").text
    assert "Góp ý cho GALS" in board
    assert 'hx-post="/phan-hoi/gop-y"' in board


def test_two_feedback_boxes_on_a_page_do_not_share_an_id(client):
    login_independent(client)
    page = client.get("/trang-ca-nhan").text
    assert page.count('id="gop-y-bang-dieu-khien"') == 1
    assert page.count('id="gop-y-chan-trang"') == 1
    assert page.count('id="gop-y-noi-dung-bang-dieu-khien"') == 1
    assert page.count('id="gop-y-noi-dung-chan-trang"') == 1


def test_log_labels_are_ascii_so_they_are_searchable(client, caplog):
    _reset_reports()
    login_independent(client)
    with caplog.at_level("INFO", logger="gals.phanhoi"):
        client.post("/phan-hoi/gop-y", data={"noi_dung": "Chữ nhỏ quá trên điện thoại"})
        client.post("/phan-hoi/bao-cao", data={"ly_do": "kho_hieu"})
    written = " ".join(r.getMessage() for r in caplog.records)
    assert "[GOP-Y]" in written
    assert "[BAO-CAO]" in written
    _reset_reports()
