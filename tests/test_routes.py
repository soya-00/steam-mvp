from __future__ import annotations

import re

from app.scenarios import all_scenarios
from tests.conftest import login_independent, login_student, login_teacher

HREF = re.compile(r'href="(/[^"#]*)"')


def test_student_pages_and_links(client):
    login_student(client)
    urls = [
        "/", "/trang-ca-nhan", "/du-an", "/ho-so", "/ho-so/chia-se",
        "/ho-so/y-tuong-tu-do", "/huy-hieu", "/tai-nguyen",
        "/dang-nhap", "/dang-ky", "/chon-avatar",
    ]
    for s in all_scenarios():
        urls += [f"/du-an/{s.id}", f"/du-an/{s.id}/khong-gian-tu-duy", f"/du-an/{s.id}/nop"]

    seen: set[str] = set()
    for u in urls:
        r = client.get(u)
        assert r.status_code == 200, u
        seen.update(HREF.findall(r.text))

    dead = [h for h in sorted(seen) if client.get(h).status_code not in (200, 303, 307)]
    assert dead == []


def test_teacher_pages_and_links(client):
    login_teacher(client)
    home = client.get("/giao-vien")
    assert home.status_code == 200

    urls = ["/giao-vien", "/giao-vien/thong-bao", "/giao-vien/tai-lieu"]
    urls += [f"/giao-vien/tai-lieu/{s.id}" for s in all_scenarios()]
    for cid in set(re.findall(r'/giao-vien/lop/(\d+)"', home.text)):
        urls.append(f"/giao-vien/lop/{cid}")
        lop = client.get(f"/giao-vien/lop/{cid}").text
        urls += [f"/giao-vien/hoc-sinh/{sid}" for sid in set(re.findall(r'/giao-vien/hoc-sinh/(\d+)"', lop))]

    seen: set[str] = set()
    for u in urls:
        r = client.get(u)
        assert r.status_code == 200, u
        seen.update(HREF.findall(r.text))

    dead = [h for h in sorted(seen) if client.get(h).status_code not in (200, 303, 307)]
    assert dead == []


def test_unknown_page_renders_404(client):
    assert client.get("/khong-ton-tai").status_code == 404


def test_teacher_dashboard_carries_the_prototype_disclaimer(client):
    login_teacher(client)
    page = client.get("/giao-vien").text
    for phrase in [
        "bản mẫu",
        "không được lưu lại",
        "đừng để học sinh nhập thông tin thật",
        "không phải công cụ hỗ trợ tâm lý",
        "LEGAL.md",
    ]:
        assert phrase.lower() in page.lower(), phrase


def test_legal_notice_exists_and_is_linked_everywhere(client):
    from pathlib import Path

    legal = Path("LEGAL.md").read_text(encoding="utf-8")
    for heading in ["Tuyên bố về bản mẫu", "Dữ liệu đi những đâu", "Trách nhiệm pháp lý"]:
        assert heading in legal, heading
    assert "111" in legal

    assert "LEGAL.md" in Path("README.md").read_text(encoding="utf-8")

    login_independent(client)
    assert "LEGAL.md" in client.get("/trang-ca-nhan").text
