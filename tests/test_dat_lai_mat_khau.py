"""Đặt lại mật khẩu.

Dịch vụ thư được thay bằng bản giả ở mọi bài — chúng chỉ kiểm phần vé, hạn
dùng và việc đuổi phiên cũ, tức là phần có thể sai trong im lặng.
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from app import dat_lai as mod
from app.db import SessionLocal
from app.models import PasswordReset, User
from tests.du_lieu_mau import SEED_EMAILS, SEED_PASSWORD
from tests.conftest import login_student

MOI = "mat-khau-moi-1"


@pytest.fixture(autouse=True)
def khong_gui_thu(monkeypatch):
    """Không bài nào được thật sự gọi ra mạng."""
    da_gui = []
    monkeypatch.setattr(
        "app.routers.auth.gui_thu",
        lambda den, tieu_de, than: da_gui.append((den, than)) or True,
    )
    return da_gui


def _user(email: str = SEED_EMAILS["hoc_sinh_co_lop"]) -> User:
    db = SessionLocal()
    try:
        return db.query(User).filter(User.email == email).first()
    finally:
        db.close()


def _xin_ve(client, email: str = SEED_EMAILS["hoc_sinh_co_lop"]):
    return client.post("/quen-mat-khau", data={"email": email}, follow_redirects=False)


def _ve_gan_nhat(khong_gui_thu) -> str:
    than = khong_gui_thu[-1][1]
    return than.split("token=")[1].split()[0]


def test_the_table_stores_a_hash_and_never_the_ticket(client, khong_gui_thu):
    _xin_ve(client)
    token = _ve_gan_nhat(khong_gui_thu)

    db = SessionLocal()
    try:
        hang = db.query(PasswordReset).one()
        assert hang.token_hash != token
        assert len(hang.token_hash) == 64
    finally:
        db.close()


def test_a_known_and_an_unknown_address_answer_identically(client):
    """Trang đăng nhập đã cẩn thận để không thành công cụ dò email. Để lộ ở
    đây thì công cốc."""
    co = _xin_ve(client)
    khong = _xin_ve(client, "khong-ai@example.com")
    assert co.status_code == khong.status_code
    assert co.headers["location"] == khong.headers["location"]

    assert client.get(co.headers["location"]).text == client.get(khong.headers["location"]).text


def test_the_ticket_sets_a_new_password(client, khong_gui_thu):
    _xin_ve(client)
    token = _ve_gan_nhat(khong_gui_thu)

    r = client.post(
        "/dat-lai-mat-khau",
        data={"token": token, "mat_khau": MOI, "mat_khau_lai": MOI},
        follow_redirects=False,
    )
    assert r.status_code == 303

    client.get("/dang-xuat")
    vao = client.post(
        "/dang-nhap",
        data={"email": SEED_EMAILS["hoc_sinh_co_lop"], "mat_khau": MOI},
        follow_redirects=False,
    )
    assert "loi=" not in vao.headers["location"]


def test_the_old_password_stops_working(client, khong_gui_thu):
    _xin_ve(client)
    client.post(
        "/dat-lai-mat-khau",
        data={"token": _ve_gan_nhat(khong_gui_thu), "mat_khau": MOI,
              "mat_khau_lai": MOI},
        follow_redirects=False,
    )
    client.get("/dang-xuat")
    r = client.post(
        "/dang-nhap",
        data={"email": SEED_EMAILS["hoc_sinh_co_lop"], "mat_khau": SEED_PASSWORD},
        follow_redirects=False,
    )
    assert "loi=sai_thong_tin" in r.headers["location"]


def test_a_ticket_works_only_once(client, khong_gui_thu):
    _xin_ve(client)
    token = _ve_gan_nhat(khong_gui_thu)
    client.post("/dat-lai-mat-khau", data={"token": token, "mat_khau": MOI, "mat_khau_lai": MOI},
                follow_redirects=False)
    lai = client.post("/dat-lai-mat-khau", data={"token": token, "mat_khau": "mat-khau-khac",
                            "mat_khau_lai": "mat-khau-khac"},
                      follow_redirects=False)
    assert "loi=ve_hong" in lai.headers["location"]


def test_an_expired_ticket_is_refused(client, khong_gui_thu):
    _xin_ve(client)
    token = _ve_gan_nhat(khong_gui_thu)
    db = SessionLocal()
    try:
        hang = db.query(PasswordReset).one()
        hang.expires_at = datetime.now() - timedelta(seconds=1)
        db.commit()
    finally:
        db.close()

    r = client.post("/dat-lai-mat-khau", data={"token": token, "mat_khau": MOI, "mat_khau_lai": MOI},
                    follow_redirects=False)
    assert "loi=ve_hong" in r.headers["location"]


def test_a_forged_ticket_is_refused(client):
    r = client.post(
        "/dat-lai-mat-khau",
        data={"token": "vé-tự-chế", "mat_khau": MOI, "mat_khau_lai": MOI},
        follow_redirects=False,
    )
    assert "loi=ve_hong" in r.headers["location"]


def test_asking_twice_kills_the_first_ticket(client, khong_gui_thu):
    _xin_ve(client)
    dau = _ve_gan_nhat(khong_gui_thu)
    _xin_ve(client)

    r = client.post("/dat-lai-mat-khau", data={"token": dau, "mat_khau": MOI, "mat_khau_lai": MOI},
                    follow_redirects=False)
    assert "loi=ve_hong" in r.headers["location"]


def test_a_weak_new_password_is_refused(client, khong_gui_thu):
    _xin_ve(client)
    r = client.post(
        "/dat-lai-mat-khau",
        data={"token": _ve_gan_nhat(khong_gui_thu), "mat_khau": "ngan",
              "mat_khau_lai": "ngan"},
        follow_redirects=False,
    )
    assert "loi=mat_khau_ngan" in r.headers["location"]


def test_a_session_minted_before_the_reset_is_thrown_out(client, khong_gui_thu):
    """Đây mới là việc chính của chức năng đặt lại: đuổi kẻ đang giữ phiên.

    Cookie phiên là chuỗi đã ký nên không thu hồi từ máy chủ được — thứ làm
    được việc đó là dấu thời gian đổi mật khẩu nằm trong chính cookie.
    """
    login_student(client)
    assert client.get("/trang-ca-nhan", follow_redirects=False).status_code == 200

    # Chủ tài khoản đặt lại mật khẩu từ một thiết bị khác. Ở đây gọi thẳng vào
    # tầng dưới để cookie của client này giữ nguyên như của kẻ đang chiếm phiên.
    _xin_ve(client)
    db = SessionLocal()
    try:
        ve = db.query(PasswordReset).filter(PasswordReset.used_at.is_(None)).one()
        mod.dat_lai(db, ve, MOI)
    finally:
        db.close()

    assert client.get("/trang-ca-nhan", follow_redirects=False).status_code == 303


def test_the_flow_works_with_no_mail_service_at_all(client, monkeypatch):
    """Chưa cấu hình dịch vụ thư thì yêu cầu vẫn phải trả lời bình thường, và
    liên kết vẫn lấy được bằng dòng lệnh."""
    monkeypatch.setattr("app.routers.auth.gui_thu", lambda *a, **k: False)
    r = _xin_ve(client)
    assert r.headers["location"] == "/quen-mat-khau?da_gui=1"

    db = SessionLocal()
    try:
        assert db.query(PasswordReset).count() == 1
    finally:
        db.close()


def test_mail_is_off_unless_both_variables_are_set(monkeypatch):
    import app.mail as mail

    monkeypatch.setattr(mail, "MAIL_API_KEY", "")
    monkeypatch.setattr(mail, "MAIL_FROM", "ai-do@gals.vn")
    assert not mail.mail_enabled()
    assert mail.gui("a@b.com", "x", "y") is False

    monkeypatch.setattr(mail, "MAIL_API_KEY", "khoa-gia")
    assert mail.mail_enabled()


def test_the_request_route_is_throttled(client):
    from app import throttle

    for _ in range(throttle.MAX_ATTEMPTS):
        _xin_ve(client)
    r = _xin_ve(client)
    assert "loi=thu_lai_sau" in r.headers["location"]


def test_an_oauth_account_may_set_a_password_this_way(client, khong_gui_thu):
    """Ai nắm hòm thư thì đã nắm luôn tài khoản Google. Từ chối ở đây không
    thêm được chút an toàn nào mà lại mất một đường cứu hộ hợp lệ."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == SEED_EMAILS["hoc_sinh_doc_lap"]).first()
        user.password_hash = None
        user.oauth_provider = "google"
        user.oauth_sub = "g-1"
        db.commit()
    finally:
        db.close()

    _xin_ve(client, SEED_EMAILS["hoc_sinh_doc_lap"])
    r = client.post(
        "/dat-lai-mat-khau",
        data={"token": _ve_gan_nhat(khong_gui_thu), "mat_khau": MOI,
              "mat_khau_lai": MOI},
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert _user(SEED_EMAILS["hoc_sinh_doc_lap"]).password_hash is not None
