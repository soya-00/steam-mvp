"""Chặn giả mạo yêu cầu từ trang khác (CSRF).

Cách làm là "gửi đôi": một giá trị ngẫu nhiên nằm trong cookie, và đúng giá
trị đó phải quay lại trong thân biểu mẫu hoặc trong một header. Trang web khác
có thể khiến trình duyệt của người dùng gửi yêu cầu kèm cookie, nhưng không
đọc được cookie của tên miền này nên không điền lại được giá trị.

Vì sao cần: mọi thao tác thay đổi dữ liệu ở đây đều là biểu mẫu POST thường —
đổi tên, giao bài, viết nhận xét, xoá. Không có lớp này thì một trang bất kỳ
có thể khiến giáo viên đang đăng nhập gửi đi một nhận xét, hoặc khiến học sinh
công khai hồ sơ của mình.
"""

from __future__ import annotations

import secrets

from starlette.middleware.base import BaseHTTPMiddleware

CSRF_COOKIE = "gals_csrf"
FORM_FIELD = "_csrf"
HEADER = "x-csrf-token"

# GET/HEAD/OPTIONS không được đổi dữ liệu, nên không cần vé.
AN_TOAN = {"GET", "HEAD", "OPTIONS", "TRACE"}


def new_token() -> str:
    return secrets.token_urlsafe(32)


async def _submitted_token(request) -> str:
    """Lấy vé từ header, hoặc từ ô ẩn trong thân biểu mẫu.

    Đọc thân yêu cầu ở đây là chuyện phải cẩn thận: dòng dữ liệu chỉ chảy được
    một lần, nên nếu đọc xong mà không trả lại thì tầng dưới nhận biểu mẫu
    rỗng và mọi trường Form(...) đều trống. Vì thế đọc xong phải phát lại.
    """
    header = request.headers.get(HEADER)
    if header:
        return header

    ctype = request.headers.get("content-type", "")
    if not ctype.startswith(("application/x-www-form-urlencoded", "multipart/form-data")):
        return ""

    body = await request.body()

    async def phat_lai():
        return {"type": "http.request", "body": body, "more_body": False}

    request._receive = phat_lai

    # request.body() đã lưu sẵn nội dung, nên form() phân tích lại từ bộ nhớ
    # chứ không đụng vào dòng dữ liệu nữa.
    form = await request.form()
    return str(form.get(FORM_FIELD) or "")


class CSRFMiddleware(BaseHTTPMiddleware):
    """Phát vé cho mọi lượt truy cập, và soát vé ở mọi phương thức ghi."""

    async def dispatch(self, request, call_next):
        from starlette.responses import PlainTextResponse

        cookie_token = request.cookies.get(CSRF_COOKIE) or ""
        token = cookie_token or new_token()
        # Bản mẫu HTML đọc giá trị này để chèn vào ô ẩn của biểu mẫu.
        request.state.csrf = token

        if request.method not in AN_TOAN:
            gui_len = await _submitted_token(request)
            # Thiếu cookie cũng là hỏng: không có gì để đối chiếu thì không thể
            # kết luận yêu cầu đến từ trang của mình.
            if not cookie_token or not secrets.compare_digest(cookie_token, gui_len):
                return PlainTextResponse(
                    "Phiên làm việc đã cũ. Bạn tải lại trang rồi thử lại nhé.",
                    status_code=403,
                )

        response = await call_next(request)
        if not cookie_token:
            response.set_cookie(
                CSRF_COOKIE,
                token,
                # Không đặt httponly: đây không phải bí mật cần giấu khỏi trang
                # của chính mình, và để mở thì kịch bản phía trình duyệt gắn
                # được vào header nếu sau này cần.
                samesite="lax",
                secure=_over_https(request),
                max_age=60 * 60 * 24 * 7,
            )
        return response


def _over_https(request) -> bool:
    from app.auth import over_https

    return over_https(request)


def csrf_context(request) -> dict:
    """Đưa vé vào mọi khung nhìn, để bản mẫu không phải tự đi lấy."""
    return {"csrf_token": getattr(request.state, "csrf", "")}
