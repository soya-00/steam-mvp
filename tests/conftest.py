from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app import throttle
from app.main import app
from app.seed import SEED_EMAILS, SEED_PASSWORD, reset_and_seed


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
