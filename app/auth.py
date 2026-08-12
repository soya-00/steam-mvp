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


def set_session(request: Request, response, user_id: int) -> None:
    response.set_cookie(
        SESSION_COOKIE,
        _serializer.dumps({"uid": user_id}),
        httponly=True,
        samesite="lax",
        secure=over_https(request),
        max_age=60 * 60 * 24 * 7,
    )


def clear_session(response) -> None:
    response.delete_cookie(SESSION_COOKIE)


def _user_id_from_request(request: Request) -> int | None:
    raw = request.cookies.get(SESSION_COOKIE)
    if not raw:
        return None
    try:
        return _serializer.loads(raw).get("uid")
    except BadSignature:
        return None


def get_current_user(
    request: Request, db: Session = Depends(get_db)
) -> User | None:
    uid = _user_id_from_request(request)
    if uid is None:
        return None
    return db.get(User, uid)


def session_key(request: Request) -> str:
    return request.cookies.get(SESSION_COOKIE, "khach")
