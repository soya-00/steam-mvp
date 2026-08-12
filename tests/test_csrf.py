"""Vé chống giả mạo yêu cầu.

Fixture `client` tự đính vé cho hơn hai trăm bài kia, nên nó không chứng minh
được gì về lớp này. Những bài dưới đây dùng `client_tho` — client trần, không
đính gì — để kiểm đúng phần chặn.
"""

from __future__ import annotations

import re
from pathlib import Path

from app.csrf import CSRF_COOKIE
from app.seed import SEED_EMAILS, SEED_PASSWORD

TEMPLATES = Path("app/templates")


def test_a_post_with_no_ticket_is_refused(client_tho):
    r = client_tho.post(
        "/dang-nhap",
        data={"email": SEED_EMAILS["hoc_sinh_co_lop"], "mat_khau": SEED_PASSWORD},
    )
    assert r.status_code == 403


def test_a_post_with_someone_elses_ticket_is_refused(client_tho):
    client_tho.get("/dang-nhap")
    r = client_tho.post(
        "/dang-nhap",
        data={
            "_csrf": "ve-tu-che-khong-khop",
            "email": SEED_EMAILS["hoc_sinh_co_lop"],
            "mat_khau": SEED_PASSWORD,
        },
    )
    assert r.status_code == 403


def test_the_matching_ticket_gets_through(client_tho):
    client_tho.get("/dang-nhap")
    ve = client_tho.cookies.get(CSRF_COOKIE)
    assert ve
    r = client_tho.post(
        "/dang-nhap",
        data={
            "_csrf": ve,
            "email": SEED_EMAILS["hoc_sinh_co_lop"],
            "mat_khau": SEED_PASSWORD,
        },
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert "loi=" not in r.headers["location"]


def test_the_header_works_too_so_htmx_buttons_are_covered(client_tho):
    """Vài chỗ đặt hx-post thẳng trên nút, không nằm trong biểu mẫu nào — chúng
    chỉ mang vé được qua header."""
    client_tho.get("/dang-nhap")
    ve = client_tho.cookies.get(CSRF_COOKIE)
    r = client_tho.post(
        "/dang-nhap",
        data={"email": SEED_EMAILS["hoc_sinh_co_lop"], "mat_khau": SEED_PASSWORD},
        headers={"X-CSRF-Token": ve},
        follow_redirects=False,
    )
    assert r.status_code == 303


def test_reading_a_page_never_needs_a_ticket(client_tho):
    for url in ["/", "/dang-nhap", "/dang-ky", "/kham-pha", "/ve-chung-toi"]:
        assert client_tho.get(url).status_code == 200, url


def test_the_form_body_survives_the_ticket_check(client_tho):
    """Đọc thân yêu cầu để lấy vé mà không phát lại thì tầng dưới nhận biểu mẫu
    rỗng, và mọi trường hoá ra trống — lỗi này im lặng, nên phải có bài canh."""
    client_tho.get("/dang-ky")
    ve = client_tho.cookies.get(CSRF_COOKIE)
    r = client_tho.post(
        "/dang-ky",
        data={
            "_csrf": ve,
            "ten": "Ngô Bảo Châu",
            "email": "chau@example.com",
            "mat_khau": "chuoi-dai-du-8",
            "tuoi": "17",
            "dong_y": "1",
        },
        follow_redirects=False,
    )
    # Nếu thân yêu cầu bị nuốt mất thì đây sẽ là loi=ten_trong.
    assert r.headers["location"] == "/chon-avatar"


def test_the_ticket_is_a_fresh_random_value_each_visit(client_tho):
    from app.csrf import new_token

    assert len({new_token() for _ in range(20)}) == 20


def test_the_cookie_is_only_issued_once_per_session(client_tho):
    client_tho.get("/")
    ve = client_tho.cookies.get(CSRF_COOKIE)
    client_tho.get("/kham-pha")
    assert client_tho.cookies.get(CSRF_COOKIE) == ve


def test_every_post_form_in_the_tree_carries_the_hidden_field():
    """Một biểu mẫu bị bỏ sót sẽ hỏng ngay khi người dùng bấm, chứ không phải
    hỏng âm thầm — nhưng chỉ hỏng đúng trang đó, nên dễ lọt qua khi xem lại."""
    thieu = []
    for path in TEMPLATES.rglob("*.html"):
        s = path.read_text(encoding="utf-8")
        for m in re.finditer(r"<form\b[^>]*?>", s, re.S):
            tag = m.group(0)
            if 'method="post"' not in tag and "hx-post" not in tag:
                continue
            sau = s[m.end() : m.end() + 200]
            if "partials/csrf.html" not in sau:
                thieu.append(f"{path}: {tag[:60]}")
    assert thieu == []


def test_the_layout_hands_every_htmx_call_the_ticket():
    base = (TEMPLATES / "base.html").read_text(encoding="utf-8")
    assert "hx-headers" in base
    assert "X-CSRF-Token" in base
