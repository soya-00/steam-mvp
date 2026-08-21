"""Đặt lại mật khẩu.

Vé là chuỗi ngẫu nhiên; bảng chỉ giữ **bản băm SHA-256** của nó. Một lần lộ cơ
sở dữ liệu vì thế không kéo theo mọi đường đặt lại đang mở.

Vé sống ba mươi phút, dùng một lần, và dùng xong thì mọi vé khác của cùng
người cũng hết giá trị.
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models import PasswordReset, User
from app.security import hash_password

SONG_PHUT = 30


def _bam(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def tao_ve(db: Session, user: User) -> str:
    """Tạo vé mới và huỷ mọi vé cũ còn treo của người này."""
    huy_ve_cu(db, user.id)
    token = secrets.token_urlsafe(32)
    db.add(
        PasswordReset(
            user_id=user.id,
            token_hash=_bam(token),
            expires_at=datetime.now() + timedelta(minutes=SONG_PHUT),
        )
    )
    db.commit()
    return token


def huy_ve_cu(db: Session, user_id: int) -> None:
    (
        db.query(PasswordReset)
        .filter(PasswordReset.user_id == user_id, PasswordReset.used_at.is_(None))
        .update({PasswordReset.used_at: datetime.now()}, synchronize_session=False)
    )
    db.commit()


def doc_ve(db: Session, token: str) -> PasswordReset | None:
    """Trả về vé nếu nó có thật, chưa dùng và chưa hết hạn."""
    if not token:
        return None
    ve = db.query(PasswordReset).filter(PasswordReset.token_hash == _bam(token)).first()
    if ve is None or ve.used_at is not None or ve.expires_at < datetime.now():
        return None
    return ve


def dat_lai(db: Session, ve: PasswordReset, mat_khau: str) -> User:
    """Đổi mật khẩu và đóng vé.

    `password_changed_at` được đóng dấu ở đây, và đó là thứ khiến mọi cookie
    phiên cũ hết giá trị — chuyện chính mà việc đặt lại tồn tại để làm.
    """
    user = db.get(User, ve.user_id)
    user.password_hash = hash_password(mat_khau)
    user.password_changed_at = datetime.now()
    ve.used_at = datetime.now()
    db.commit()
    return user


def than_thu(lien_ket: str) -> tuple[str, str]:
    return (
        "Đặt lại mật khẩu GALS",
        (
            "Chào bạn,\n\n"
            "Có người vừa yêu cầu đặt lại mật khẩu cho tài khoản GALS dùng địa chỉ này.\n"
            f"Nếu là bạn, mở liên kết dưới đây trong vòng {SONG_PHUT} phút:\n\n"
            f"{lien_ket}\n\n"
            "Nếu không phải bạn thì bỏ qua thư này — mật khẩu hiện tại vẫn nguyên.\n"
        ),
    )
