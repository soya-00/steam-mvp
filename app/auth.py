from __future__ import annotations

from fastapi import Depends, Request
from itsdangerous import BadSignature, URLSafeSerializer
from sqlalchemy.orm import Session

from app.config import SECRET_KEY, SESSION_COOKIE
from app.db import get_db
from app.models import User

_serializer = URLSafeSerializer(SECRET_KEY, salt="gals-session")


def over_https(request: Request) -> bool:
    """Bật cờ Secure khi đang chạy thật, nhưng vẫn cho chạy HTTP ở máy cá nhân.

    Render đứng trước ứng dụng và chuyển tiếp giao thức gốc qua
    X-Forwarded-Proto, nên chỉ nhìn request.url.scheme là thấy 'http'.
    """
    forwarded = request.headers.get("x-forwarded-proto", "")
    if forwarded:
        return forwarded.split(",")[0].strip() == "https"
    return request.url.scheme == "https"


def _pw_stamp(user) -> str:
    return user.password_changed_at.isoformat() if user and user.password_changed_at else ""


def set_session(request: Request, response, user_id: int, user=None) -> None:
    response.set_cookie(
        SESSION_COOKIE,
        _serializer.dumps({"uid": user_id, "pw": _pw_stamp(user)}),
        httponly=True,
        samesite="lax",
        secure=over_https(request),
        max_age=60 * 60 * 24 * 7,
    )


def clear_session(response) -> None:
    response.delete_cookie(SESSION_COOKIE)


def _payload(request: Request) -> dict:
    raw = request.cookies.get(SESSION_COOKIE)
    if not raw:
        return {}
    try:
        data = _serializer.loads(raw)
    except BadSignature:
        return {}
    return data if isinstance(data, dict) else {}


def _user_id_from_request(request: Request) -> int | None:
    return _payload(request).get("uid")


def get_current_user(
    request: Request, db: Session = Depends(get_db)
) -> User | None:
    data = _payload(request)
    uid = data.get("uid")
    if uid is None:
        return None
    user = db.get(User, uid)
    if user is None:
        return None
    # Cookie phát trước lần đổi mật khẩu gần nhất coi như hết giá trị. Đây là
    # cách duy nhất đuổi được kẻ đang giữ phiên cũ, vì cookie đã ký thì không
    # thu hồi từ phía máy chủ được.
    if data.get("pw", "") != _pw_stamp(user):
        return None
    return user


def session_key(request: Request) -> str:
    return request.cookies.get(SESSION_COOKIE, "khach")
