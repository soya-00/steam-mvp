from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app import throttle
from app.csrf import CSRF_COOKIE, FORM_FIELD
from app.main import app
from app.seed import SEED_EMAILS, SEED_PASSWORD, reset_and_seed


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


@pytest.fixture()
def client():
    # Khởi động ứng dụng chỉ gieo dữ liệu khi bảng còn trống, nên nếu để nguyên
    # thì mỗi bài kiểm thử lại thừa hưởng dữ liệu của bài trước. Ở đây xoá sạch
    # rồi gieo lại để từng bài chạy trên một cơ sở dữ liệu giống hệt nhau.
    reset_and_seed()
    # Bộ đếm số lần thử hỏng nằm trong bộ nhớ tiến trình, nên nó sống lâu hơn
    # cả cơ sở dữ liệu: không xoá thì bài nào thử sai mật khẩu sẽ làm bài sau
    # bị khoá.
    throttle.reset_all()
    with TestClient(app) as c:
        _mang_ve_csrf(c)
        yield c


@pytest.fixture()
def client_tho():
    """Client không tự đính vé — dùng để kiểm chính lớp CSRF."""
    reset_and_seed()
    throttle.reset_all()
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


def login_student(c: TestClient) -> None:
    _login(c, "hoc_sinh_co_lop")


def login_independent(c: TestClient) -> None:
    _login(c, "hoc_sinh_doc_lap")


def login_teacher(c: TestClient) -> None:
    _login(c, "giao_vien")
