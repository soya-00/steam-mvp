"""Vào lớp, rời lớp, gỡ khỏi lớp, đổi mã, đóng lớp.

Mọi thay đổi về thành viên lớp đi qua đúng file này. Lý do: việc một người có
đọc được bài của một người khác hay không được quyết định ở đây, nên nó phải
nằm một chỗ để đọc hết trong một lần, chứ không rải ra mấy router.
"""

from __future__ import annotations

import random
import string
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import Class, ClassMembership, User


def lop_theo_ma(db: Session, ma: str) -> Class | None:
    """Tìm lớp theo mã. Lớp đã đóng thì coi như không tìm thấy."""
    code = (ma or "").strip().upper()
    if not code:
        return None
    lop = db.query(Class).filter(Class.class_code == code).first()
    if lop is None or lop.da_dong:
        return None
    return lop


def da_o_trong(db: Session, user: User, class_id: int) -> bool:
    return (
        db.query(ClassMembership.id)
        .filter(
            ClassMembership.student_id == user.id,
            ClassMembership.class_id == class_id,
        )
        .first()
        is not None
    )


def vao_lop(db: Session, user: User, lop: Class) -> bool:
    """Thêm học sinh vào lớp. Trả về False nếu đã ở trong rồi.

    Gọi lại lần nữa không tạo thêm hàng — người dùng bấm hai lần là chuyện
    bình thường, và bảng chưa có ràng buộc duy nhất.
    """
    if da_o_trong(db, user, lop.id):
        return False
    db.add(ClassMembership(student_id=user.id, class_id=lop.id))
    db.commit()
    return True


def roi_lop(db: Session, user: User, class_id: int) -> bool:
    """Học sinh tự rời lớp. Có hiệu lực ngay, không cần ai duyệt.

    Chính sách riêng tư nói rời lớp là cách rút lại đồng ý cho giáo viên đọc
    bài. Một quyền phải xin phép người khác mới dùng được thì không còn là
    quyền, nên ở đây không có hàng đợi duyệt.

    Chỉ xoá tư cách thành viên. Bài viết, hồ sơ và huy hiệu của em vẫn nguyên —
    những thứ đó chưa bao giờ thuộc về lớp.
    """
    hang = (
        db.query(ClassMembership)
        .filter(
            ClassMembership.student_id == user.id,
            ClassMembership.class_id == class_id,
        )
        .first()
    )
    if hang is None:
        return False
    db.delete(hang)
    db.commit()
    return True


def go_khoi_lop(db: Session, class_id: int, student_id: int) -> bool:
    """Giáo viên gỡ một học sinh khỏi lớp mình.

    Người gọi phải kiểm tra lớp có thuộc giáo viên đó không trước khi gọi —
    hàm này không tự kiểm quyền.
    """
    hang = (
        db.query(ClassMembership)
        .filter(
            ClassMembership.student_id == student_id,
            ClassMembership.class_id == class_id,
        )
        .first()
    )
    if hang is None:
        return False
    db.delete(hang)
    db.commit()
    return True


_BANG_CHU = string.ascii_uppercase + string.digits


def ma_lop_moi(db: Session) -> str:
    """Sinh mã lớp chưa ai dùng.

    Chỗ cũ thử 50 lần rồi trả về một mã 6 ký tự **không kiểm trùng** — hiếm,
    nhưng khi trùng thì hỏng ở tầng ràng buộc duy nhất của cơ sở dữ liệu, tức
    là giáo viên thấy lỗi 500 lúc tạo lớp. Ở đây nới dần độ dài rồi thử tiếp,
    nên không có nhánh nào trả về mã chưa kiểm.
    """
    for do_dai in (4, 5, 6, 8):
        for _ in range(50):
            ma = "GALS-" + "".join(random.choice(_BANG_CHU) for _ in range(do_dai))
            if db.query(Class.id).filter(Class.class_code == ma).first() is None:
                return ma
    raise RuntimeError("Không sinh được mã lớp mới sau nhiều lần thử.")


def tao_lop(db: Session, giao_vien: User, ten: str) -> Class:
    """Lớp mới. `roster_prefix` đóng băng ở mã đầu tiên và không đổi nữa."""
    ma = ma_lop_moi(db)
    lop = Class(
        teacher_id=giao_vien.id,
        class_code=ma,
        roster_prefix=ma,
        name=ten,
        school_id=giao_vien.school_id,
    )
    db.add(lop)
    db.commit()
    db.refresh(lop)
    return lop


def doi_ten(db: Session, lop: Class, ten: str) -> None:
    lop.name = ten
    db.commit()


def doi_ma(db: Session, lop: Class) -> str:
    """Cấp mã mới cho lớp. Mã cũ hết tác dụng ngay.

    Dùng khi mã bị chụp màn hình hoặc chuyền ra ngoài. Không đụng tới danh
    sách thành viên: những em đã vào vẫn ở trong lớp.
    """
    lop.class_code = ma_lop_moi(db)
    db.commit()
    return lop.class_code


def dong_lop(db: Session, lop: Class) -> None:
    """Đóng lớp: không nhận thêm ai, mã hết tác dụng, bài cũ vẫn đọc được.

    Cố ý không có xoá lớp. Trong một đợt thử nghiệm thì không nên có nút nào
    huỷ được dữ liệu thật.
    """
    lop.dong_luc = datetime.now()
    db.commit()


def mo_lai_lop(db: Session, lop: Class) -> None:
    lop.dong_luc = None
    db.commit()
