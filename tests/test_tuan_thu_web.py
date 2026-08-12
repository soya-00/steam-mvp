"""Tuân thủ ở mức trang web: văn bản pháp lý, bằng chứng đồng ý, quyền được
xoá, và mấy header rẻ tiền mà hay bị quên."""

from __future__ import annotations

import re
from pathlib import Path

from app.csrf import CSRF_COOKIE
from app.db import SessionLocal
from app.models import Consent, User, YeuCauXoa
from app.seed import SEED_EMAILS
from tests.conftest import login_independent, login_student, login_teacher

TRANG_PHAP_LY = ["/chinh-sach-rieng-tu", "/dieu-khoan"]


def test_the_two_documents_have_pages_of_their_own(client):
    """Liên kết ra GitHub không phải là "có chính sách trên trang" — người dùng
    phải đọc được ngay tại chỗ."""
    for url in TRANG_PHAP_LY:
        r = client.get(url)
        assert r.status_code == 200, url


def test_both_documents_are_linked_from_every_page(client):
    login_student(client)
    for url in ["/", "/kham-pha", "/ve-chung-toi", "/trang-ca-nhan", "/ho-so", "/dang-nhap"]:
        page = client.get(url).text
        for muc in TRANG_PHAP_LY:
            assert muc in page, f"{url} thiếu {muc}"


def test_the_privacy_page_names_who_runs_gals(client):
    """PDPL cần một đầu mối có tên để gửi yêu cầu về dữ liệu cá nhân."""
    page = client.get("/chinh-sach-rieng-tu").text
    assert "Ai đứng sau GALS" in page


def test_the_privacy_page_names_the_same_ai_vendor_as_legal_md(client):
    """Trang chính sách không được lệch khỏi LEGAL.md về chuyện dữ liệu ra
    nước ngoài. Đổi nhà cung cấp mà quên một trong hai chỗ là bài này đỏ."""
    page = client.get("/chinh-sach-rieng-tu").text
    legal = Path("LEGAL.md").read_text(encoding="utf-8")

    ten_nha_cung_cap = ["OpenAI", "Google", "Gemini"]
    tren_trang = {t for t in ten_nha_cung_cap if t in page}
    trong_legal = {t for t in ten_nha_cung_cap if t in legal}

    assert tren_trang, "Trang chính sách không nêu nhà cung cấp AI nào."
    assert tren_trang & trong_legal, f"Trang nói {tren_trang}, LEGAL.md nói {trong_legal}."


def test_the_privacy_page_lists_exactly_what_the_browser_stores(client):
    page = client.get("/chinh-sach-rieng-tu").text
    for thu in ["Cookie đăng nhập", "chống giả mạo", "Cài đặt hiển thị"]:
        assert thu in page, thu


def test_the_notice_bar_makes_no_promise_it_cannot_keep(client):
    """Không có nút "Từ chối", vì ở đây chẳng có gì để từ chối — chỉ có cookie
    đăng nhập, vé chống giả mạo và cài đặt hiển thị. Một nút từ chối không tắt
    được gì là một lời hứa suông."""
    page = client.get("/").text
    assert "thong-bao-luu-tru" in page
    assert "Đã hiểu" in page
    assert "Từ chối" not in page


def test_no_third_party_script_or_tracker_is_loaded(client):
    """Cả câu chuyện thông báo lưu trữ đứng được là nhờ điều này."""
    for url in ["/", "/kham-pha", "/dang-nhap"]:
        page = client.get(url).text
        for nguon in re.findall(r'<script[^>]+src="([^"]+)"', page):
            assert nguon.startswith("/static/"), f"{url}: {nguon}"
        for nguon in re.findall(r'<link[^>]+href="([^"]+)"[^>]*rel="stylesheet"', page):
            assert nguon.startswith("/static/"), f"{url}: {nguon}"


def test_signing_up_without_agreeing_creates_nothing(client):
    r = client.post(
        "/dang-ky",
        data={
            "ten": "Ngô Bảo Châu",
            "email": "chau@example.com",
            "mat_khau": "chuoi-dai-du-8",
            "tuoi": "17",
        },
        follow_redirects=False,
    )
    assert "loi=chua_dong_y" in r.headers["location"]

    db = SessionLocal()
    try:
        assert db.query(User).filter(User.email == "chau@example.com").first() is None
    finally:
        db.close()


def test_agreeing_leaves_a_record_with_the_version(client):
    """PDPL đòi chứng minh được đã có đồng ý. Một ô tích không để lại dấu vết
    thì không chứng minh được gì."""
    client.post(
        "/dang-ky",
        data={
            "ten": "Ngô Bảo Châu",
            "email": "chau@example.com",
            "mat_khau": "chuoi-dai-du-8",
            "tuoi": "17",
            "dong_y": "1",
        },
        follow_redirects=False,
    )
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "chau@example.com").first()
        rows = db.query(Consent).filter(Consent.user_id == user.id).all()
        assert {r.loai for r in rows} == {"rieng_tu", "dieu_khoan"}
        assert all(r.phien_ban and r.dong_y_luc for r in rows)
    finally:
        db.close()


def test_the_consent_record_stores_no_ip_address():
    """Địa chỉ máy tự nó đã là dữ liệu cá nhân, mà cặp phiên bản + thời điểm
    đã đủ chứng minh."""
    cot = {c.name for c in Consent.__table__.columns}
    assert not {"ip", "ip_address", "dia_chi_ip"} & cot


def test_a_student_can_ask_for_deletion_and_change_their_mind(client):
    login_independent(client)
    client.post("/tai-khoan/yeu-cau-xoa", data={"ly_do": "Mình không dùng nữa"})

    db = SessionLocal()
    try:
        assert db.query(YeuCauXoa).filter(YeuCauXoa.xu_ly_luc.is_(None)).count() == 1
    finally:
        db.close()

    assert "đã gửi yêu cầu xoá" in client.get("/tai-khoan").text.lower()

    client.post("/tai-khoan/huy-yeu-cau-xoa", data={})
    db = SessionLocal()
    try:
        assert db.query(YeuCauXoa).count() == 0
    finally:
        db.close()


def test_asking_twice_does_not_queue_two_requests(client):
    login_independent(client)
    client.post("/tai-khoan/yeu-cau-xoa", data={})
    client.post("/tai-khoan/yeu-cau-xoa", data={})
    db = SessionLocal()
    try:
        assert db.query(YeuCauXoa).count() == 1
    finally:
        db.close()


def test_the_account_page_says_what_deletion_cannot_reach(client):
    """Bản tổng hợp giáo viên đã tải về máy thì rời khỏi hệ thống từ lúc bấm
    tải. Nói trước, chứ không để người dùng phát hiện sau."""
    login_independent(client)
    page = client.get("/tai-khoan").text
    assert "tải bản tổng hợp" in page or "đã tải" in page


def test_deleting_for_real_leaves_no_dangling_rows(client):
    """Feedback và PortfolioEntry không nằm trong cascade của User, nên xoá mà
    quên hai bảng này là để lại hàng trỏ vào tài khoản không còn tồn tại."""
    from app.models import Feedback, PortfolioEntry
    from app.quan_tri import main

    login_student(client)
    email = SEED_EMAILS["hoc_sinh_co_lop"]

    db = SessionLocal()
    try:
        uid = db.query(User).filter(User.email == email).first().id
        assert db.query(PortfolioEntry).filter(PortfolioEntry.student_id == uid).count() > 0
    finally:
        db.close()

    assert main(["xoa", email, "--chac-chan"]) == 0

    db = SessionLocal()
    try:
        assert db.query(User).filter(User.email == email).first() is None
        assert db.query(PortfolioEntry).filter(PortfolioEntry.student_id == uid).count() == 0
        assert db.query(Feedback).filter(Feedback.student_id == uid).count() == 0
    finally:
        db.close()


def test_deletion_needs_the_confirmation_flag(client):
    from app.quan_tri import main

    assert main(["xoa", SEED_EMAILS["hoc_sinh_co_lop"]]) == 1
    db = SessionLocal()
    try:
        assert db.query(User).filter(User.email == SEED_EMAILS["hoc_sinh_co_lop"]).first()
    finally:
        db.close()


def test_the_security_headers_are_on_every_response(client):
    r = client.get("/")
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert r.headers["X-Frame-Options"] == "DENY"
    assert "default-src 'self'" in r.headers["Content-Security-Policy"]
    assert "frame-ancestors 'none'" in r.headers["Content-Security-Policy"]


def test_hsts_is_absent_over_plain_http(client):
    """Gửi HSTS trên HTTP ở máy cá nhân sẽ khoá cứng localhost sang https
    trong chính trình duyệt của mình."""
    assert "Strict-Transport-Security" not in client.get("/").headers


def test_hsts_appears_once_the_proxy_says_https(client):
    r = client.get("/", headers={"X-Forwarded-Proto": "https"})
    assert "max-age=" in r.headers["Strict-Transport-Security"]


def test_the_csrf_cookie_is_marked_secure_behind_https(client_tho):
    r = client_tho.get("/", headers={"X-Forwarded-Proto": "https"})
    assert "Secure" in r.headers["set-cookie"], r.headers["set-cookie"]


def test_the_session_cookie_is_marked_secure_behind_https():
    """Cookie phiên đã ký mà thiếu cờ Secure thì bị tước xuống HTTP được.

    Kiểm thẳng hàm thay vì qua HTTP: TestClient chạy trên http://, nên nó
    không gửi lại một cookie đã có cờ Secure và vòng đăng nhập không đi hết được.
    """
    from fastapi import Request
    from fastapi.responses import RedirectResponse

    from app.auth import over_https, set_session

    def _req(proto: str) -> Request:
        return Request(
            {
                "type": "http", "method": "GET", "path": "/", "query_string": b"",
                "headers": [(b"x-forwarded-proto", proto.encode())],
                "scheme": "http", "server": ("testserver", 80),
            }
        )

    assert over_https(_req("https"))
    assert not over_https(_req("http"))

    r = RedirectResponse("/", status_code=303)
    set_session(_req("https"), r, 1)
    assert "Secure" in r.headers["set-cookie"]

    r = RedirectResponse("/", status_code=303)
    set_session(_req("http"), r, 1)
    assert "Secure" not in r.headers["set-cookie"]


def test_cookies_stay_usable_over_plain_http_for_local_work(client_tho):
    r = client_tho.get("/")
    assert "Secure" not in r.headers.get("set-cookie", "")
