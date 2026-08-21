from __future__ import annotations

import re

import pytest
from fastapi.testclient import TestClient

from app import throttle
from app.csrf import CSRF_COOKIE, FORM_FIELD
from app.main import app
from tests.du_lieu_mau import SEED_EMAILS, SEED_PASSWORD, reset_and_seed


def _mang_ve_csrf(c: TestClient) -> None:
    """Cho client kiểm thử cư xử giống trình duyệt về khoản vé CSRF.

    Trình duyệt thật luôn tải trang trước, nhận cookie, rồi gửi lại vé trong ô
    ẩn của biểu mẫu. Client kiểm thử thì gọi thẳng POST. Thay vì sửa hai trăm
    bài để tự đính vé, gói lại một lần ở đây — còn việc CSRF có thật sự chặn
    hay không thì tests/test_csrf.py kiểm bằng client trần.
    """
    c.get("/")
    goc = c.post

    def post(url, **kwargs):
        ve = c.cookies.get(CSRF_COOKIE)
        if ve and "data" in kwargs and isinstance(kwargs["data"], dict):
            kwargs["data"] = {FORM_FIELD: ve, **kwargs["data"]}
        elif ve:
            kwargs.setdefault("headers", {}).setdefault("X-CSRF-Token", ve)
        return goc(url, **kwargs)

    c.post = post


@pytest.fixture(autouse=True)
def _co_so_du_lieu_sach():
    """Xoá sạch rồi gieo lại, đúng một lần cho mỗi bài kiểm thử.

    Phải là fixture riêng chứ không nằm trong `client`: bài nào dùng cả
    `client` lẫn `client_tho` sẽ gieo lại hai lần, và lần thứ hai xoá mất
    những gì bài vừa dựng. Kiểu hỏng đó biểu hiện ra rất xa chỗ gây ra nó.
    """
    reset_and_seed()
    # Bộ đếm số lần thử hỏng nằm trong bộ nhớ tiến trình, nên nó sống lâu hơn
    # cả cơ sở dữ liệu: không xoá thì bài nào thử sai mật khẩu sẽ làm bài sau
    # bị khoá.
    throttle.reset_all()


@pytest.fixture()
def client():
    with TestClient(app) as c:
        _mang_ve_csrf(c)
        yield c


@pytest.fixture()
def client_tho():
    """Client không tự đính vé — dùng để kiểm chính lớp CSRF, và để đóng vai
    một thiết bị thứ hai giữ cookie cũ."""
    with TestClient(app) as c:
        yield c


def _login(c: TestClient, key: str) -> None:
    """Đăng nhập thật, qua đúng biểu mẫu mà người dùng dùng.

    Trước đây có đường tắt /demo/{tài khoản} vào thẳng không cần mật khẩu. Bỏ
    rồi — và vì các hàm trợ giúp ở đây giữ nguyên tên, hơn hai trăm bài kiểm
    thử gọi chúng không phải sửa gì.
    """
    r = c.post(
        "/dang-nhap",
        data={"email": SEED_EMAILS[key], "mat_khau": SEED_PASSWORD},
        follow_redirects=False,
    )
    assert r.status_code == 303, r.status_code
    assert "loi=" not in r.headers.get("location", ""), r.headers.get("location")
    _chon_khong_gian(c)


def _chon_khong_gian(c: TestClient) -> None:
    """Chọn bối cảnh đầu tiên, giống người dùng thật vừa đăng nhập.

    Bảng điều khiển hỏi "hôm nay bạn làm ở đâu" trước khi mở, nên nếu không
    chọn thì mọi bài kiểm thử sẽ nhận trang hỏi thay vì trang cần xem. Lựa chọn
    đầu tiên là lớp của người đó, tức đúng phạm vi mà các bài vẫn giả định.
    """
    page = c.get("/chon-khong-gian")
    if page.status_code != 200:
        return
    khoa = re.findall(r'name="khoa" value="([^"]+)"', page.text)
    if khoa:
        c.post("/chon-khong-gian", data={"khoa": khoa[0]}, follow_redirects=False)


def login_student(c: TestClient) -> None:
    _login(c, "hoc_sinh_co_lop")


def login_independent(c: TestClient) -> None:
    _login(c, "hoc_sinh_doc_lap")


def login_teacher(c: TestClient) -> None:
    _login(c, "giao_vien")
