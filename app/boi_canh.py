"""Chọn bối cảnh làm việc: một lớp cụ thể, hay việc cá nhân.

Một học sinh có thể ở nhiều lớp, và bài tự làm thì chẳng thuộc lớp nào. Trước
đây bảng điều khiển trộn hết vào một chỗ, nên "việc của mình" và "việc cô
giao" nằm lẫn nhau. Chọn một lần rồi nhớ, đổi bằng một điều khiển trên đầu
trang.

Lựa chọn nằm trong cookie thường chứ không ký: giá trị duy nhất người dùng có
thể bịa ra là số hiệu một lớp, và `doc()` luôn đối chiếu lại với danh sách lớp
mà người đó thật sự thuộc về. Ký thêm cũng không thay đổi được điều gì.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models import Class, ClassMembership, User

COOKIE = "gals_boi_canh"
CA_NHAN = "ca-nhan"
TAT_CA = "tat-ca"  # chỉ dành cho giáo viên


@dataclass(frozen=True)
class BoiCanh:
    khoa: str                 # "ca-nhan" | "tat-ca" | "lop:<id>"
    ten: str
    class_id: int | None = None

    @property
    def la_ca_nhan(self) -> bool:
        return self.class_id is None and self.khoa == CA_NHAN


def lop_cua_hoc_sinh(db: Session, user: User) -> list[Class]:
    return (
        db.query(Class)
        .join(ClassMembership, ClassMembership.class_id == Class.id)
        .filter(ClassMembership.student_id == user.id)
        .order_by(Class.name)
        .all()
    )


def lop_cua_giao_vien(db: Session, user: User) -> list[Class]:
    # Lớp đã đóng không nằm trong danh sách chọn: nó vẫn mở đọc được từ trang
    # lớp, nhưng chọn nó làm không gian làm việc hôm nay thì không còn nghĩa gì.
    return (
        db.query(Class)
        .filter(Class.teacher_id == user.id, Class.dong_luc.is_(None))
        .order_by(Class.name)
        .all()
    )


def lua_chon(db: Session, user: User) -> list[BoiCanh]:
    """Những bối cảnh người này được phép chọn."""
    if user.is_teacher:
        return [BoiCanh(TAT_CA, "Tất cả lớp")] + [
            BoiCanh(f"lop:{c.id}", c.name, c.id) for c in lop_cua_giao_vien(db, user)
        ]
    return [
        BoiCanh(f"lop:{c.id}", c.name, c.id) for c in lop_cua_hoc_sinh(db, user)
    ] + [BoiCanh(CA_NHAN, "Việc cá nhân")]


def mac_dinh(db: Session, user: User) -> BoiCanh:
    return BoiCanh(TAT_CA, "Tất cả lớp") if user.is_teacher else BoiCanh(CA_NHAN, "Việc cá nhân")


def doc(request, db: Session, user: User) -> BoiCanh:
    """Bối cảnh đang chọn, đã đối chiếu với quyền thật.

    Rời lớp xong thì cookie cũ trỏ vào một lớp không còn thuộc về mình — lúc
    đó rơi về mặc định chứ không lỗi.
    """
    khoa = request.cookies.get(COOKIE, "")
    for bc in lua_chon(db, user):
        if bc.khoa == khoa:
            return bc
    return mac_dinh(db, user)


def da_chon(request, db: Session, user: User) -> bool:
    khoa = request.cookies.get(COOKIE, "")
    return any(bc.khoa == khoa for bc in lua_chon(db, user))


def can_hoi(request, db: Session, user: User) -> bool:
    """Chỉ hỏi khi thật sự có gì để chọn.

    Học sinh chưa vào lớp nào thì câu hỏi chỉ có một đáp án — hỏi là làm phiền.
    """
    if da_chon(request, db, user):
        return False
    return len(lua_chon(db, user)) > 1


def ghi(request, response, bc: BoiCanh) -> None:
    from app.auth import over_https

    response.set_cookie(
        COOKIE,
        bc.khoa,
        httponly=True,
        samesite="lax",
        secure=over_https(request),
        max_age=60 * 60 * 24 * 30,
    )
