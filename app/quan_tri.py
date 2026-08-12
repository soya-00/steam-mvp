"""Việc quản trị chạy bằng dòng lệnh, cố ý không có đường HTTP nào.

Cấp mã cho trường, đình chỉ tài khoản, đặt lại mật khẩu, xoá tài khoản theo
yêu cầu — toàn những việc nguy hiểm. Không có route thì không có gì để tấn
công từ ngoài, không cần thêm vai trò quản trị, không cần mô hình phân quyền,
và ở quy mô vài trường thì đây là cách trung thực nhất.

    python -m app.quan_tri truong-them "THPT Chu Văn An" --tinh "Hà Nội"
    python -m app.quan_tri truong-liet-ke
    python -m app.quan_tri ma "THPT Chu Văn An"
    python -m app.quan_tri ma-ai "THPT Chu Văn An"
    python -m app.quan_tri khoa co.mai@truong.edu.vn
    python -m app.quan_tri mo-khoa co.mai@truong.edu.vn
    python -m app.quan_tri dat-lai co.mai@truong.edu.vn
    python -m app.quan_tri xoa-cho    # xem các yêu cầu xoá đang chờ
    python -m app.quan_tri xoa hocsinh@example.com
"""

from __future__ import annotations

import argparse
import sys

from app.dat_lai import tao_ve
from app.db import SessionLocal
from app.models import (
    Feedback,
    PortfolioEntry,
    School,
    User,
    YeuCauXoa,
)
from app.schools import cap_ma_moi, giao_vien_theo_ma, ma_con_han


def _truong(db, ten: str) -> School | None:
    return db.query(School).filter(School.ten == ten).first()


def _nguoi(db, email: str) -> User | None:
    return db.query(User).filter(User.email == email.strip().lower()).first()


def truong_them(db, args) -> int:
    if _truong(db, args.ten) is not None:
        print(f"Đã có trường tên '{args.ten}'.")
        return 1
    db.add(School(ten=args.ten, tinh_thanh=args.tinh, lien_he_email=args.email))
    db.commit()
    print(f"Đã thêm '{args.ten}'. Cấp mã bằng: python -m app.quan_tri ma \"{args.ten}\"")
    return 0


def truong_liet_ke(db, args) -> int:
    rows = db.query(School).order_by(School.ten).all()
    if not rows:
        print("Chưa có trường nào.")
        return 0
    for t in rows:
        han = "còn hạn" if ma_con_han(t) else "hết hạn / chưa cấp"
        trang_thai = "đang hoạt động" if t.hoat_dong else "đã tắt"
        print(f"[{t.id}] {t.ten} — {trang_thai}, mã {han}")
    return 0


def ma(db, args) -> int:
    truong = _truong(db, args.ten)
    if truong is None:
        print(f"Không tìm thấy trường '{args.ten}'.")
        return 1
    code = cap_ma_moi(db, truong)
    print(f"Mã mới cho '{truong.ten}': {code}")
    print(f"Hết hạn: {truong.ma_het_han:%d/%m/%Y %H:%M}")
    print("Mã cũ (nếu có) đã hết tác dụng ngay lúc này.")
    return 0


def ma_ai(db, args) -> int:
    """Ai đã lập tài khoản trong cửa sổ mã hiện tại — câu hỏi đầu tiên khi lộ mã."""
    truong = _truong(db, args.ten)
    if truong is None:
        print(f"Không tìm thấy trường '{args.ten}'.")
        return 1
    rows = giao_vien_theo_ma(db, truong)
    if not rows:
        print("Chưa ai lập tài khoản trong cửa sổ mã hiện tại.")
        return 0
    for u in rows:
        print(f"{u.email} — {u.name} — {u.created_at:%d/%m/%Y %H:%M} — {u.status}")
    return 0


def _doi_status(db, email: str, status: str) -> int:
    user = _nguoi(db, email)
    if user is None:
        print(f"Không tìm thấy tài khoản '{email}'.")
        return 1
    user.status = status
    db.commit()
    print(f"{user.email} → {status}")
    return 0


def khoa(db, args) -> int:
    return _doi_status(db, args.email, "tam_khoa")


def mo_khoa(db, args) -> int:
    return _doi_status(db, args.email, "hoat_dong")


def dat_lai(db, args) -> int:
    """In ra liên kết đặt lại. Đường cứu hộ khi chưa có dịch vụ thư, và cũng
    là đường duy nhất cho người gõ nhầm địa chỉ email lúc đăng ký."""
    user = _nguoi(db, args.email)
    if user is None:
        print(f"Không tìm thấy tài khoản '{args.email}'.")
        return 1
    token = tao_ve(db, user)
    print(f"Liên kết cho {user.email} (sống 30 phút):")
    print(f"  {args.goc.rstrip('/')}/dat-lai-mat-khau?token={token}")
    return 0


def xoa_cho(db, args) -> int:
    rows = (
        db.query(YeuCauXoa)
        .filter(YeuCauXoa.xu_ly_luc.is_(None))
        .order_by(YeuCauXoa.tao_luc)
        .all()
    )
    if not rows:
        print("Không có yêu cầu xoá nào đang chờ.")
        return 0
    for r in rows:
        u = db.get(User, r.user_id)
        print(f"{u.email} — {u.name} — xin từ {r.tao_luc:%d/%m/%Y}")
        if r.ly_do:
            print(f"    lý do: {r.ly_do}")
    return 0


def xoa(db, args) -> int:
    """Xoá thật, không phải cắm cờ.

    Một cột 'đã xoá' mà vẫn giữ nguyên bài viết chính là thứ mà quyền được xoá
    sinh ra để ngăn.
    """
    user = _nguoi(db, args.email)
    if user is None:
        print(f"Không tìm thấy tài khoản '{args.email}'.")
        return 1

    if not args.chac_chan:
        print(f"Sẽ xoá vĩnh viễn: {user.email} ({user.name}).")
        print("Thêm --chac-chan nếu đúng ý bạn.")
        return 1

    # Hai bảng này không nằm trong cascade của User, nên phải dọn tay — bỏ sót
    # là để lại hàng trỏ vào một tài khoản không còn tồn tại.
    db.query(Feedback).filter(
        (Feedback.student_id == user.id) | (Feedback.teacher_id == user.id)
    ).delete(synchronize_session=False)
    db.query(PortfolioEntry).filter(PortfolioEntry.student_id == user.id).delete(
        synchronize_session=False
    )
    db.query(YeuCauXoa).filter(YeuCauXoa.user_id == user.id).delete(
        synchronize_session=False
    )
    email = user.email
    db.delete(user)
    db.commit()
    print(f"Đã xoá {email}.")
    print("Lưu ý: bản tải về mà giáo viên đã lưu trên máy thì không với tới được.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m app.quan_tri")
    sub = parser.add_subparsers(dest="lenh", required=True)

    p = sub.add_parser("truong-them", help="Thêm một trường đối tác")
    p.add_argument("ten")
    p.add_argument("--tinh", default="")
    p.add_argument("--email", default="")
    p.set_defaults(func=truong_them)

    p = sub.add_parser("truong-liet-ke", help="Liệt kê các trường")
    p.set_defaults(func=truong_liet_ke)

    p = sub.add_parser("ma", help="Cấp mã giáo viên mới (3 ngày), ghi đè mã cũ")
    p.add_argument("ten")
    p.set_defaults(func=ma)

    p = sub.add_parser("ma-ai", help="Ai đã lập tài khoản trong cửa sổ mã hiện tại")
    p.add_argument("ten")
    p.set_defaults(func=ma_ai)

    p = sub.add_parser("khoa", help="Đình chỉ một tài khoản")
    p.add_argument("email")
    p.set_defaults(func=khoa)

    p = sub.add_parser("mo-khoa", help="Bỏ đình chỉ")
    p.add_argument("email")
    p.set_defaults(func=mo_khoa)

    p = sub.add_parser("dat-lai", help="In liên kết đặt lại mật khẩu")
    p.add_argument("email")
    p.add_argument("--goc", default="http://localhost:8000", help="Gốc địa chỉ trang")
    p.set_defaults(func=dat_lai)

    p = sub.add_parser("xoa-cho", help="Các yêu cầu xoá đang chờ")
    p.set_defaults(func=xoa_cho)

    p = sub.add_parser("xoa", help="Xoá vĩnh viễn một tài khoản")
    p.add_argument("email")
    p.add_argument("--chac-chan", action="store_true", dest="chac_chan")
    p.set_defaults(func=xoa)

    args = parser.parse_args(argv)
    db = SessionLocal()
    try:
        return args.func(db, args)
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
