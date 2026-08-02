from __future__ import annotations

import re

from app.scenarios import all_scenarios
from tests.conftest import login_independent, login_student, login_teacher

IMG = re.compile(r"<img[^>]*>")
INPUT = re.compile(r'<(?:input|textarea|select)[^>]*\bid="([^"]+)"')


def test_field_artwork_is_decorative_everywhere(client):
    login_student(client)
    urls = ["/trang-ca-nhan", "/du-an", "/huy-hieu"]
    urls += [f"/du-an/{s.id}" for s in all_scenarios()]
    for u in urls:
        page = client.get(u).text
        for img in IMG.findall(page):
            if "/static/img/fields/" in img:
                assert 'aria-hidden="true"' in img and 'alt=""' in img, (u, img[:120])


def test_skip_link_and_landmarks(client):
    login_student(client)
    page = client.get("/trang-ca-nhan").text
    assert "Bỏ qua phần điều hướng" in page
    assert 'id="noi-dung"' in page and 'tabindex="-1"' in page
    assert 'aria-current="page"' in client.get("/du-an").text


def test_chat_log_is_a_live_region(client):
    login_student(client)
    page = client.get("/ho-so/y-tuong-tu-do").text
    assert 'aria-live="polite"' in page and 'role="log"' in page


def test_stepper_state_is_spoken_not_only_colour(client):
    # Học sinh độc lập không có dữ liệu gieo sẵn, nên tình huống luôn ở trạng
    # thái đang làm dở — không phụ thuộc vào seed của tài khoản demo có lớp.
    login_independent(client)
    sid = all_scenarios()[0].id
    client.get(f"/du-an/{sid}/khong-gian-tu-duy")
    page = client.get(f"/du-an/{sid}/khong-gian-tu-duy").text
    assert 'aria-label="Tiến độ' in page
    assert "đang làm" in page and "chưa tới" in page


def test_every_form_control_has_a_label(client):
    login_student(client)
    for u in ["/dang-nhap", "/dang-ky", "/ho-so/y-tuong-tu-do"]:
        page = client.get(u).text
        for control_id in INPUT.findall(page):
            assert f'for="{control_id}"' in page, (u, control_id)


def test_print_materials_contain_no_artwork(client):
    login_teacher(client)
    for s in all_scenarios():
        page = client.get(f"/giao-vien/tai-lieu/{s.id}").text
        assert "/static/img/fields/" not in page
        assert "Hướng dẫn nhanh cho thầy cô" in page
        assert "không bắt buộc" in page
