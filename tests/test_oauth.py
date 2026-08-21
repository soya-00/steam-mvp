"""Đăng nhập bằng Google / Microsoft.

Vòng chuyển hướng thật không kiểm được ở đây: không có khoá của nhà cung cấp,
và địa chỉ gọi lại cần một tên miền công khai. Cái kiểm được — và cũng là chỗ
duy nhất dễ sai đến mức nguy hiểm — là **thứ tự nối tài khoản**.
"""

from __future__ import annotations

import pytest

from app import oauth
from app.db import SessionLocal
from app.models import User
from tests.du_lieu_mau import SEED_EMAILS


@pytest.fixture()
def db(client):
    s = SessionLocal()
    try:
        yield s
    finally:
        s.close()


def _info(sub="sub-1", email="ai-do@example.com", verified=True, name="Người Mới"):
    return {"sub": sub, "email": email, "email_verified": verified, "name": name}


def test_a_returning_person_is_matched_by_provider_id_not_email(db):
    """Trường học đổi địa chỉ email của học sinh là chuyện thường. `sub` thì
    không đổi, nên nó phải là khoá nối chính."""
    dau = oauth.noi_tai_khoan(db, "google", _info(email="cu@truong.edu.vn"))
    lai = oauth.noi_tai_khoan(db, "google", _info(email="moi@truong.edu.vn"))
    assert lai.id == dau.id
    assert db.query(User).filter(User.oauth_sub == "sub-1").count() == 1


def test_an_unverified_email_never_takes_over_an_existing_account(db):
    """Ở một nhà cung cấp lỏng lẻo, ai cũng khai được email của người khác.
    Khớp theo email chưa xác thực là đưa thẳng tài khoản cho họ."""
    nan_nhan = db.query(User).filter(User.email == SEED_EMAILS["hoc_sinh_co_lop"]).first()

    ke_la = oauth.noi_tai_khoan(
        db, "google", _info(email=SEED_EMAILS["hoc_sinh_co_lop"], verified=False)
    )
    assert ke_la.id != nan_nhan.id

    db.refresh(nan_nhan)
    assert nan_nhan.oauth_sub is None


def test_a_verified_email_joins_the_existing_account(db):
    goc = db.query(User).filter(User.email == SEED_EMAILS["hoc_sinh_co_lop"]).first()
    noi = oauth.noi_tai_khoan(
        db, "google", _info(email=SEED_EMAILS["hoc_sinh_co_lop"], verified=True)
    )
    assert noi.id == goc.id
    assert noi.oauth_provider == "google"
    assert noi.oauth_sub == "sub-1"


def test_one_providers_account_cannot_claim_anothers(db):
    """Đã gắn Google rồi thì một sub Microsoft trùng email không được chiếm chỗ."""
    da_gan = oauth.noi_tai_khoan(db, "google", _info(sub="g-1", email="chung@example.com"))
    khac = oauth.noi_tai_khoan(db, "microsoft", _info(sub="m-1", email="chung@example.com"))
    assert khac.id != da_gan.id


def test_a_person_with_no_email_still_gets_an_account(db):
    nguoi = oauth.noi_tai_khoan(db, "microsoft", _info(sub="m-2", email="", verified=False))
    assert nguoi.id is not None
    assert nguoi.oauth_sub == "m-2"
    # Cột email là duy nhất, nên phải có gì đó — miễn là không đụng ai khác.
    nua = oauth.noi_tai_khoan(db, "microsoft", _info(sub="m-3", email="", verified=False))
    assert nua.email != nguoi.email


def test_a_new_oauth_account_is_a_student_not_a_teacher(db):
    """Tài khoản giáo viên chỉ đến từ mã của trường. Nếu Google cấp được thì
    toàn bộ phần canh giữ ở /dang-ky/giao-vien thành vô nghĩa."""
    nguoi = oauth.noi_tai_khoan(db, "google", _info(sub="g-99"))
    assert nguoi.role == "student"
    assert nguoi.school_id is None


def test_signing_in_stamps_the_time(db):
    nguoi = oauth.noi_tai_khoan(db, "google", _info(sub="g-2"))
    assert nguoi.last_login_at is not None


def test_claims_with_no_subject_are_rejected():
    assert oauth.doc_userinfo({}) is None
    assert oauth.doc_userinfo({"email": "ai-do@example.com"}) is None
    assert oauth.doc_userinfo({"sub": "x"})["sub"] == "x"


def test_a_missing_verified_flag_counts_as_unverified():
    """Microsoft không phải lúc nào cũng gửi email_verified. Đoán rộng ra ở đây
    chính là chỗ hỏng, nên thiếu thì coi như chưa xác thực."""
    assert oauth.doc_userinfo({"sub": "x", "email": "a@b.com"})["email_verified"] is False
    assert oauth.doc_userinfo({"sub": "x", "email_verified": True})["email_verified"] is True


def test_email_is_lowercased_before_it_is_matched_on():
    assert oauth.doc_userinfo({"sub": "x", "email": "A@B.COM"})["email"] == "a@b.com"


def test_a_provider_with_no_credentials_renders_no_button(client, monkeypatch):
    assert "Tiếp tục với Google" not in client.get("/dang-nhap").text
    assert client.get("/dang-nhap/google", follow_redirects=False).headers["location"] == "/dang-nhap"


def test_a_configured_provider_shows_up(client, monkeypatch):
    monkeypatch.setitem(oauth.NHA_CUNG_CAP["google"], "client_id", "gia-lap")
    monkeypatch.setitem(oauth.NHA_CUNG_CAP["google"], "client_secret", "gia-lap")
    page = client.get("/dang-nhap").text
    assert "Tiếp tục với Google" in page
    assert "Tiếp tục với Microsoft" not in page


def test_no_client_secret_is_ever_committed():
    """Khoá chỉ sống trong bảng biến môi trường của nơi triển khai."""
    import subprocess

    # Ghép từ hai mảnh, nếu không thì chính file này sẽ khớp với chính nó.
    tien_to = "GOCSPX" + "-"

    theo_doi = subprocess.run(
        ["git", "ls-files"], capture_output=True, text=True, check=True
    ).stdout.split()
    for ten in theo_doi:
        if ten.endswith((".py", ".html", ".json", ".yaml", ".yml", ".md")):
            noi_dung = open(ten, encoding="utf-8", errors="ignore").read()
            assert tien_to not in noi_dung, ten
