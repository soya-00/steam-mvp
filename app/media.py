from __future__ import annotations

from urllib.parse import urlparse

MAX_URL_CHARS = 500

ALLOWED_SCHEMES = ("http", "https")

ERRORS = {
    "scheme": (
        "Đường dẫn phải bắt đầu bằng http:// hoặc https://. "
        "Bạn thử dán lại link từ thanh địa chỉ của trình duyệt nhé."
    ),
    "host": "Đường dẫn này thiếu tên trang web nên mình chưa nhận được.",
    "too_long": "Đường dẫn dài quá. Bạn dùng link ngắn hơn giúp mình nhé.",
    "credentials": "Đường dẫn có chứa thông tin đăng nhập nên mình không nhận.",
}


def validate_url(raw: str) -> tuple[str, str | None]:
    url = (raw or "").strip()
    if not url:
        return "", None

    if len(url) > MAX_URL_CHARS:
        return "", ERRORS["too_long"]

    try:
        parsed = urlparse(url)
    except ValueError:
        return "", ERRORS["scheme"]

    if parsed.scheme.lower() not in ALLOWED_SCHEMES:
        return "", ERRORS["scheme"]
    if not parsed.netloc:
        return "", ERRORS["host"]
    if parsed.username or parsed.password:
        return "", ERRORS["credentials"]

    return url, None
