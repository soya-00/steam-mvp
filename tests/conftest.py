from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.seed import reset_and_seed


@pytest.fixture()
def client():
    # Khởi động ứng dụng chỉ gieo dữ liệu khi bảng còn trống, nên nếu để nguyên
    # thì mỗi bài kiểm thử lại thừa hưởng dữ liệu của bài trước. Ở đây xoá sạch
    # rồi gieo lại để từng bài chạy trên một cơ sở dữ liệu giống hệt nhau.
    reset_and_seed()
    with TestClient(app) as c:
        yield c


def login_student(c: TestClient) -> None:
    c.get("/demo/hoc_sinh_co_lop")


def login_independent(c: TestClient) -> None:
    c.get("/demo/hoc_sinh_doc_lap")


def login_teacher(c: TestClient) -> None:
    c.get("/demo/giao_vien")
