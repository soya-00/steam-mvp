"""Gửi thư qua API HTTPS của nhà cung cấp, không phải SMTP.

Nơi triển khai chặn các cổng SMTP đi ra để không thành chỗ phát tán thư rác,
nên `smtplib` sẽ treo chứ không báo lỗi tử tế. Gọi API qua HTTPS thì tránh
được hẳn chuyện đó, và `httpx` vốn đã có sẵn trong danh sách phụ thuộc.

Chưa cấu hình biến môi trường thì `gui()` trả về False và phần gọi tự biết
đường xử lý — không nuốt lỗi, cũng không giả vờ là đã gửi.

Việc thật sự tốn công không nằm ở đây mà ở DNS: thư gửi từ một tên miền chưa
xác thực sẽ vào hòm thư rác hoặc bị chặn thẳng, nên phải có bản ghi SPF và
DKIM cho tên miền gửi trước đã.
"""

from __future__ import annotations

import logging
import os

log = logging.getLogger("gals.mail")

MAIL_API_KEY = os.getenv("MAIL_API_KEY", "").strip()
MAIL_FROM = os.getenv("MAIL_FROM", "").strip()
MAIL_API_URL = os.getenv("MAIL_API_URL", "https://api.resend.com/emails").strip()


def mail_enabled() -> bool:
    return bool(MAIL_API_KEY and MAIL_FROM)


def gui(den: str, tieu_de: str, noi_dung: str) -> bool:
    """Gửi một lá thư thuần văn bản. Trả về True nếu nhà cung cấp đã nhận."""
    if not mail_enabled():
        log.warning("Chưa cấu hình MAIL_API_KEY — không gửi thư tới %s.", den)
        return False

    import httpx

    try:
        r = httpx.post(
            MAIL_API_URL,
            headers={"Authorization": f"Bearer {MAIL_API_KEY}"},
            json={"from": MAIL_FROM, "to": [den], "subject": tieu_de, "text": noi_dung},
            timeout=10,
        )
        r.raise_for_status()
        return True
    except Exception as e:  # noqa: BLE001 — hỏng thư không được làm sập yêu cầu
        # Không ghi địa chỉ vào nhật ký: nhật ký không phải chỗ chứa dữ liệu cá nhân.
        log.warning("Gửi thư hỏng: %s", type(e).__name__)
        return False
