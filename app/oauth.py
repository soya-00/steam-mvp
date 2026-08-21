"""Đăng nhập bằng tài khoản Google hoặc Microsoft.

Phần đáng nói duy nhất ở đây là thứ tự nối tài khoản, nên nó nằm riêng trong
`noi_tai_khoan()` và có bài kiểm thử riêng: nối sai thứ tự là đường để một
người mượn tài khoản của người khác.

Không khoá nào nằm trong kho mã. Nhà cung cấp nào chưa có biến môi trường thì
nút của nhà cung cấp đó không hiện, giống hệt cách `gemini_enabled()` làm.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.config import (
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    MICROSOFT_CLIENT_ID,
    MICROSOFT_CLIENT_SECRET,
    MICROSOFT_TENANT,
)
from app.models import User

NHA_CUNG_CAP = {
    "google": {
        "ten": "Google",
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "metadata_url": "https://accounts.google.com/.well-known/openid-configuration",
    },
    "microsoft": {
        "ten": "Microsoft",
        "client_id": MICROSOFT_CLIENT_ID,
        "client_secret": MICROSOFT_CLIENT_SECRET,
        "metadata_url": (
            f"https://login.microsoftonline.com/{MICROSOFT_TENANT}"
            "/v2.0/.well-known/openid-configuration"
        ),
    },
}


def bat(ten: str) -> bool:
    """Nhà cung cấp này đã cấu hình đủ chưa."""
    cau_hinh = NHA_CUNG_CAP.get(ten)
    return bool(cau_hinh and cau_hinh["client_id"] and cau_hinh["client_secret"])


def dang_bat() -> list[dict]:
    return [{"key": k, "ten": v["ten"]} for k, v in NHA_CUNG_CAP.items() if bat(k)]


def oauth_san_sang() -> bool:
    return bool(dang_bat())


_oauth = None


def khach():
    """Dựng đối tượng Authlib một lần, và chỉ khi thật sự cần."""
    global _oauth
    if _oauth is None:
        from authlib.integrations.starlette_client import OAuth

        _oauth = OAuth()
        for key in NHA_CUNG_CAP:
            if not bat(key):
                continue
            c = NHA_CUNG_CAP[key]
            _oauth.register(
                name=key,
                client_id=c["client_id"],
                client_secret=c["client_secret"],
                server_metadata_url=c["metadata_url"],
                client_kwargs={"scope": "openid email profile"},
            )
    return _oauth


def doc_userinfo(claims: dict) -> dict | None:
    """Rút ra ba thứ cần dùng, và bỏ qua nếu thiếu định danh.

    `email_verified` của Microsoft không phải lúc nào cũng có; thiếu thì coi
    như chưa xác thực, vì đoán rộng ra ở đây chính là chỗ hỏng.
    """
    sub = str(claims.get("sub") or "").strip()
    if not sub:
        return None
    email = str(claims.get("email") or "").strip().lower()
    verified = claims.get("email_verified")
    return {
        "sub": sub,
        "email": email,
        "email_verified": verified is True or verified == "true",
        "name": str(claims.get("name") or "").strip() or "Người dùng mới",
    }


def noi_tai_khoan(db: Session, provider: str, info: dict) -> User:
    """Tìm đúng tài khoản, hoặc tạo mới. Thứ tự dưới đây là phần quan trọng.

    1. Khớp theo (nhà cung cấp, sub). `sub` là định danh ổn định phía nhà cung
       cấp — trường học đổi địa chỉ email của học sinh là chuyện thường, còn
       `sub` thì không đổi.
    2. Khớp theo email **đã được xác thực**, và chỉ khi tài khoản đó chưa gắn
       với nhà cung cấp nào khác.
    3. Hết thì tạo mới.

    Không bao giờ khớp theo email chưa xác thực. Ai cũng khai được email của
    người khác ở một nhà cung cấp lỏng lẻo; khớp theo đó là đưa thẳng tài
    khoản cho họ.
    """
    user = (
        db.query(User)
        .filter(User.oauth_provider == provider, User.oauth_sub == info["sub"])
        .first()
    )
    if user is None and info["email"] and info["email_verified"]:
        ung_vien = db.query(User).filter(User.email == info["email"]).first()
        if ung_vien is not None and ung_vien.oauth_sub in (None, "", info["sub"]):
            user = ung_vien
            user.oauth_provider = provider
            user.oauth_sub = info["sub"]

    if user is None:
        # Chỉ nhận địa chỉ thật khi nó đã xác thực **và** chưa thuộc về ai. Cột
        # email là duy nhất, nên nếu cứ lấy bừa thì hai trường hợp cùng hỏng:
        # địa chỉ đã có chủ sẽ làm vỡ ràng buộc, còn địa chỉ chưa xác thực thì
        # chiếm mất chỗ của người thật sự sở hữu nó sau này.
        email = info["email"] if info["email"] and info["email_verified"] else ""
        if email and db.query(User.id).filter(User.email == email).first() is not None:
            email = ""
        user = User(
            name=info["name"][:60],
            # Người dùng vẫn đăng nhập được bằng chính nhà cung cấp, vì khoá nối
            # là (provider, sub) chứ không phải email.
            email=email or f"{provider}:{info['sub']}",
            role="student",
            oauth_provider=provider,
            oauth_sub=info["sub"],
        )
        db.add(user)

    user.last_login_at = datetime.now()
    db.commit()
    db.refresh(user)
    return user
