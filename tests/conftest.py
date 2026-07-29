from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


def login_student(c: TestClient) -> None:
    c.get("/demo/hoc_sinh_co_lop")


def login_independent(c: TestClient) -> None:
    c.get("/demo/hoc_sinh_doc_lap")


def login_teacher(c: TestClient) -> None:
    c.get("/demo/giao_vien")
