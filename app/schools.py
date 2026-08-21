"""Trường đối tác và mã dành cho giáo viên.

Toàn bộ việc canh giữ tài khoản giáo viên nằm ở đây, cố ý gom vào một chỗ:
tài khoản giáo viên là tài khoản đọc được nhật ký của trẻ, nên thứ cấp nó
không thể là một ô chọn trong biểu mẫu.

Mã sống ba ngày. Cửa sổ tự đóng, không cần tác vụ dọn dẹp nào chạy nền, và
hạn dùng được kiểm ngay cạnh chỗ so mã — không tách ra hai nơi, vì tách ra là
lúc người ta quên mất một nơi.
"""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models import School, User

MA_SONG_NGAY = 3
_BANG_CHU = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # bỏ I, O, 0, 1 cho khỏi đọc nhầm


def sinh_ma(do_dai: int = 10) -> str:
    return "".join(secrets.choice(_BANG_CHU) for _ in range(do_dai))


def truong_dang_nhan(db: Session) -> list[School]:
    """Danh sách cho ô chọn trường. Chỉ trường đang hoạt động."""
    return db.query(School).filter(School.hoat_dong.is_(True)).order_by(School.ten).all()


def ma_con_han(truong: School, bay_gio: datetime | None = None) -> bool:
    if not truong.hoat_dong or not truong.ma_giao_vien or truong.ma_het_han is None:
        return False
    return (bay_gio or datetime.now()) < truong.ma_het_han


def truong_theo_ma(db: Session, school_id: int | None, ma: str) -> School | None:
    """Trả về trường nếu mã khớp **và** còn hạn. Sai một trong hai thì None.

    So mã bằng compare_digest để thời gian trả lời không tiết lộ đã đúng được
    mấy ký tự đầu.
    """
    ma = (ma or "").strip().upper()
    if not school_id or not ma:
        return None
    truong = db.get(School, school_id)
    if truong is None or not ma_con_han(truong):
        return None
    if not secrets.compare_digest(truong.ma_giao_vien or "", ma):
        return None
    return truong


def cap_ma_moi(db: Session, truong: School, songay: int = MA_SONG_NGAY) -> str:
    """Cấp mã mới, ghi đè mã cũ.

    Ghi đè chính là cách thu hồi một mã bị lộ trước khi nó hết ba ngày.
    """
    ma = sinh_ma()
    truong.ma_giao_vien = ma
    truong.ma_het_han = datetime.now() + timedelta(days=songay)
    db.commit()
    return ma


def giao_vien_theo_ma(db: Session, truong: School) -> list[User]:
    """Ai đã lập tài khoản trong cửa sổ hiện tại của trường này.

    Hết hạn chỉ chặn việc lập thêm tài khoản; nó không thu hồi được tài khoản
    đã lập. Khi một mã bị lộ thì đây là câu hỏi cần trả lời ngay, nên nó phải
    là một truy vấn chứ không phải một buổi dò tay.
    """
    tu = (truong.ma_het_han or datetime.now()) - timedelta(days=MA_SONG_NGAY)
    return (
        db.query(User)
        .filter(
            User.school_id == truong.id,
            User.role == "teacher",
            User.created_at >= tu,
        )
        .order_by(User.created_at)
        .all()
    )
