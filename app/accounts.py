"""Tạo và tìm tài khoản.

Router chỉ nhận dữ liệu từ biểu mẫu rồi gọi xuống đây, để phần quyết định
"lời này có được dùng làm tên không", "email này đã có chưa" nằm một chỗ và
kiểm thử được mà không cần dựng HTTP.

Mọi lỗi trả về đều là **mã ngắn**, không phải câu tiếng Việt. Câu chữ được
tra ở `LOI` khi vẽ trang. Lý do rất cụ thể: chỗ cũ nhét thẳng câu trả lời của
bộ lọc vào URL chuyển hướng, mà câu trả lời cho trường hợp khủng hoảng dài
mấy trăm ký tự và có xuống dòng — vừa hỏng header, vừa đem một lời nhắn về
đường dây 111 đi dán vào ô báo lỗi của ô nhập tên.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import User
from app.moderation import OK as SCREEN_OK
from app.moderation import screen
from app.security import hash_password, password_problem

MAX_NAME = 60
MIN_AGE = 16

LOI = {
    "thieu": "Điền giúp mình đủ tên, email và mật khẩu nhé.",
    "ten_trong": "Tên không được để trống.",
    "ten_bi_chan": "Tên này chưa dùng được. Bạn đổi sang tên khác nhé.",
    "email_hong": "Email này trông chưa đúng.",
    "email_trung": "Email này đã có tài khoản rồi. Bạn đăng nhập nhé.",
    "mat_khau_ngan": "Mật khẩu cần ít nhất 8 ký tự.",
    "mat_khau_toan_so": "Mật khẩu toàn số dễ đoán. Thêm chữ vào nhé.",
    "mat_khau_dai": "Mật khẩu dài quá.",
    "tuoi_hong": "Bạn điền số tuổi giúp mình nhé.",
    "sai_thong_tin": "Email hoặc mật khẩu chưa đúng.",
    "thu_lai_sau": "Bạn thử sai nhiều lần rồi. Chờ ít phút rồi thử lại nhé.",
    "ma_lop_sai": "Không tìm thấy lớp nào có mã này.",
    "ma_giao_vien_sai": "Mã này không dùng được. Nhờ trường liên hệ với GALS để lấy mã mới.",
    "truong_sai": "Bạn chọn trường giúp mình nhé.",
    "chua_dong_y": "Bạn cần đồng ý với hai văn bản trước khi tạo tài khoản.",
    "ve_hong": "Liên kết này đã hết hạn hoặc đã dùng rồi. Bạn xin liên kết mới nhé.",
}


def message_for(code: str | None) -> str | None:
    """Đổi mã lỗi thành câu tiếng Việt. Mã lạ thì bỏ qua, không hiện gì."""
    if not code:
        return None
    return LOI.get(code)


def normalise_email(raw: str) -> str:
    return (raw or "").strip().lower()


def email_looks_wrong(email: str) -> bool:
    # Không cố kiểm tra email có thật hay không — chuyện đó chỉ hộp thư trả lời
    # được. Ở đây chỉ chặn những gì chắc chắn không phải địa chỉ.
    if len(email) > 200 or email.count("@") != 1:
        return True
    local, _, domain = email.partition("@")
    return not local or not domain or "." not in domain or " " in email


def clean_name(raw: str) -> tuple[str | None, str | None]:
    """Trả về (tên đã gọn, mã lỗi). Một trong hai luôn là None."""
    name = " ".join((raw or "").split())[:MAX_NAME]
    if not name:
        return None, "ten_trong"
    verdict, _ = screen(name)
    if verdict != SCREEN_OK:
        # Mọi phán quyết khác OK đều gom về một lời từ chối ngắn. Ô nhập tên
        # không phải chỗ để trả lời một tin nhắn khủng hoảng.
        return None, "ten_bi_chan"
    return name, None


_MAT_KHAU_LOI = {
    "ngan": "mat_khau_ngan",
    "dai": "mat_khau_dai",
    "so": "mat_khau_toan_so",
}


def check_password(raw: str) -> str | None:
    problem = password_problem(raw or "")
    if problem is None:
        return None
    if "ít nhất" in problem:
        return _MAT_KHAU_LOI["ngan"]
    if "dài quá" in problem:
        return _MAT_KHAU_LOI["dai"]
    return _MAT_KHAU_LOI["so"]


def parse_age(raw: str) -> int | None:
    try:
        age = int((raw or "").strip())
    except ValueError:
        return None
    return age if 5 <= age <= 100 else None


def email_taken(db: Session, email: str) -> bool:
    return db.query(User.id).filter(User.email == email).first() is not None


def find_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def create_user(
    db: Session,
    *,
    name: str,
    email: str,
    password: str,
    role: str = "student",
    school_id: int | None = None,
) -> User:
    user = User(
        name=name,
        email=email,
        role=role,
        password_hash=hash_password(password),
        school_id=school_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
