"""Đếm số lần thử hỏng, để chặn dò mật khẩu và dò mã giáo viên.

Bộ đếm nằm trong bộ nhớ tiến trình: khởi động lại là mất sạch. Đó là đánh đổi
có chủ ý — chừng nào phiên đăng nhập còn nằm trong cookie chứ chưa nằm trong
cơ sở dữ liệu thì thêm một bảng chỉ để đếm là thừa. Khi nào chạy nhiều tiến
trình cùng lúc thì phải chuyển sang kho dùng chung, vì lúc đó mỗi tiến trình
chỉ đếm được phần của mình.

Số khoá bị chặn trên để một kẻ tấn công không thể làm phình bộ nhớ bằng cách
gửi vô số email khác nhau — đúng cách `app/gemini.py` đã làm với hạn mức tin
nhắn.
"""

from __future__ import annotations

import time

MAX_KEYS = 2000
# Sau ngần này lần sai liên tiếp thì khoá, và khoá trong ngần này giây.
MAX_ATTEMPTS = 8
COOLDOWN_SECONDS = 15 * 60

# khoá -> (số lần sai, thời điểm lần sai gần nhất)
_attempts: dict[str, tuple[int, float]] = {}


def _prune() -> None:
    if len(_attempts) < MAX_KEYS:
        return
    for stale in list(_attempts)[: MAX_KEYS // 2]:
        del _attempts[stale]


def _current(key: str) -> tuple[int, float]:
    count, last = _attempts.get(key, (0, 0.0))
    if count and time.monotonic() - last > COOLDOWN_SECONDS:
        # Hết thời gian phạt thì coi như chưa từng sai.
        _attempts.pop(key, None)
        return 0, 0.0
    return count, last


def blocked(key: str) -> bool:
    count, _ = _current(key)
    return count >= MAX_ATTEMPTS


def record_failure(key: str) -> None:
    count, _ = _current(key)
    if key not in _attempts:
        _prune()
    _attempts[key] = (count + 1, time.monotonic())


def clear(key: str) -> None:
    """Gọi sau khi thành công, để một lần gõ nhầm không đọng lại."""
    _attempts.pop(key, None)


def reset_all() -> None:
    """Chỉ dùng trong kiểm thử — mỗi bài phải bắt đầu từ bộ đếm rỗng."""
    _attempts.clear()
