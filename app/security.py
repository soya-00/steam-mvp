"""Băm mật khẩu.

Argon2id là lựa chọn mặc định hiện nay cho mật khẩu người dùng: nó tốn cả bộ
nhớ lẫn thời gian, nên card đồ hoạ không rút ngắn được việc dò như với bcrypt.

Toàn bộ phần còn lại của ứng dụng chỉ gọi ba hàm dưới đây và không bao giờ
chạm tới thư viện băm trực tiếp — đổi thuật toán sau này thì sửa đúng file này.
"""

from __future__ import annotations

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

# Mật khẩu ngắn hơn 8 ký tự không nên tồn tại; dài hơn 200 thì chỉ là cách
# làm nghẽn máy chủ, vì Argon2 băm cả chuỗi.
MIN_PASSWORD = 8
MAX_PASSWORD = 200

_hasher = PasswordHasher()


def hash_password(raw: str) -> str:
    return _hasher.hash(raw)


def verify_password(raw: str, stored: str | None) -> bool:
    """Đúng/sai, không bao giờ ném lỗi ra ngoài.

    Chữ ký hàm phải như nhau dù tài khoản có tồn tại hay không, nếu không thời
    gian phản hồi sẽ tiết lộ email nào đã đăng ký.
    """
    if not stored:
        # Tài khoản đăng nhập bằng Google chưa đặt mật khẩu. Vẫn băm một lần
        # cho tốn thời gian tương đương, rồi trả về sai.
        _hasher.hash(raw or "khong-co-mat-khau")
        return False
    try:
        return _hasher.verify(stored, raw)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def needs_rehash(stored: str) -> bool:
    """Tham số của Argon2 sẽ tăng theo thời gian; băm lại khi người dùng đăng
    nhập là cách duy nhất nâng cấp mà không cần biết mật khẩu gốc."""
    try:
        return _hasher.check_needs_rehash(stored)
    except InvalidHashError:
        return True


def password_problem(raw: str) -> str | None:
    """Trả về lý do bằng tiếng Việt, hoặc None nếu mật khẩu dùng được."""
    if len(raw) < MIN_PASSWORD:
        return f"Mật khẩu cần ít nhất {MIN_PASSWORD} ký tự."
    if len(raw) > MAX_PASSWORD:
        return "Mật khẩu dài quá."
    if raw.isdigit():
        return "Mật khẩu toàn số dễ đoán. Thêm chữ vào nhé."
    return None
