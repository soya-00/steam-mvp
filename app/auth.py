"""Xác thực GIẢ LẬP cho prototype.

Bất kỳ email/mật khẩu nào cũng đăng nhập được vào tài khoản học sinh mặc định.
Không có mật khẩu thật, không băm, không khôi phục mật khẩu — đúng như §6.
Phiên đăng nhập là một cookie đã ký (itsdangerous) chỉ chứa user id.
"""

from __future__ import annotations

from fastapi import Depends, Request
from itsdangerous import BadSignature, URLSafeSerializer
from sqlalchemy.orm import Session

from app.config import SECRET_KEY, SESSION_COOKIE
from app.db import get_db
from app.models import User

_serializer = URLSafeSerializer(SECRET_KEY, salt="gals-session")

# Khoá tra cứu ba tài khoản demo (nút "Demo nhanh" ở màn hình đăng nhập).
DEMO_ACCOUNTS = {
    "giao_vien": "co.mai@gals.demo",
    "hoc_sinh_co_lop": "linh@gals.demo",
    "hoc_sinh_doc_lap": "trang@gals.demo",
}

DEFAULT_STUDENT_EMAIL = DEMO_ACCOUNTS["hoc_sinh_co_lop"]


def set_session(response, user_id: int) -> None:
    response.set_cookie(
        SESSION_COOKIE,
        _serializer.dumps({"uid": user_id}),
        httponly=True,
        samesite="lax",
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
    """Trả về User đang đăng nhập, hoặc None. Không tự chuyển hướng."""
    uid = _user_id_from_request(request)
    if uid is None:
        return None
    return db.get(User, uid)


def session_key(request: Request) -> str:
    """Khoá dùng cho trần số lượt chat trong bộ nhớ."""
    return request.cookies.get(SESSION_COOKIE, "khach")
