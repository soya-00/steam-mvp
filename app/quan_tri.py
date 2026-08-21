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
    python -m app.quan_tri doi-email cu@example.com moi@example.com
    python -m app.quan_tri xoa-cho    # xem các yêu cầu xoá đang chờ
    python -m app.quan_tri xoa hocsinh@example.com
    python -m app.quan_tri sao-luu sao-luu-2026-08-13.json
    python -m app.quan_tri phuc-hoi sao-luu-2026-08-13.json --chac-chan
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path

from sqlalchemy import inspect

from app.dat_lai import tao_ve
from app.db import Base, SessionLocal, engine
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


def doi_email(db, args) -> int:
    """Đổi địa chỉ thư của một tài khoản.

    Đường cứu hộ cho người gõ nhầm email lúc đăng ký và không đăng nhập được để
    tự sửa — họ đang gõ địa chỉ họ *tưởng* mình đã dùng, nên cả đăng nhập lẫn
    đặt lại mật khẩu đều không tới được.
    """
    user = _nguoi(db, args.email_cu)
    if user is None:
        print(f"Không tìm thấy tài khoản '{args.email_cu}'.")
        return 1

    moi = args.email_moi.strip().lower()
    if _nguoi(db, moi) is not None:
        print(f"Địa chỉ '{moi}' đã có tài khoản khác dùng.")
        return 1

    cu = user.email
    user.email = moi
    db.commit()
    print(f"{cu} → {moi}")
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


PHIEN_BAN_SAO_LUU = 1


def _json_an_toan(value):
    if isinstance(value, datetime):
        return {"__kieu__": "datetime", "gia_tri": value.isoformat()}
    if isinstance(value, date):
        return {"__kieu__": "date", "gia_tri": value.isoformat()}
    if isinstance(value, bytes):
        raise TypeError("Không sao lưu được cột nhị phân — chưa bảng nào có.")
    return value


def _doc_lai(value):
    if isinstance(value, dict) and "__kieu__" in value:
        if value["__kieu__"] == "datetime":
            return datetime.fromisoformat(value["gia_tri"])
        return date.fromisoformat(value["gia_tri"])
    return value


def _thu_tu_bang() -> list:
    """Bảng cha trước bảng con, để phục hồi không vướng khoá ngoại."""
    return Base.metadata.sorted_tables


def sao_luu(db, args) -> int:
    """Đổ toàn bộ cơ sở dữ liệu ra một tệp JSON.

    Đây là tuyến thứ hai nằm dưới bản sao lưu tự động của nhà cung cấp, không
    phải để thay thế nó. Giá trị thật của nó là làm cho việc *diễn tập phục
    hồi* trở nên khả thi: đổ ra, nạp vào một cơ sở dữ liệu trống, đếm lại số
    hàng — không phải đụng vào bản chạy thật lần nào. Một bản sao lưu chưa
    thử phục hồi thì chưa phải bản sao lưu.

    Tệp này chứa **toàn bộ dữ liệu cá nhân**, kể cả nhật ký của học sinh và mã
    băm mật khẩu. Nó phải được giữ như chính cơ sở dữ liệu: không đưa lên kho
    mã, không gửi qua ứng dụng nhắn tin, và xoá khi không cần nữa.
    """
    duong_dan = Path(args.tep)
    if duong_dan.exists() and not args.ghi_de:
        print(f"'{duong_dan}' đã tồn tại. Thêm --ghi-de nếu đúng ý bạn.")
        return 1

    du_lieu: dict[str, list[dict]] = {}
    for bang in _thu_tu_bang():
        rows = db.execute(bang.select()).mappings().all()
        du_lieu[bang.name] = [
            {k: _json_an_toan(v) for k, v in row.items()} for row in rows
        ]

    goi = {
        "phien_ban": PHIEN_BAN_SAO_LUU,
        "tao_luc": datetime.now().isoformat(),
        "bang": du_lieu,
    }
    duong_dan.write_text(json.dumps(goi, ensure_ascii=False), encoding="utf-8")

    tong = sum(len(v) for v in du_lieu.values())
    print(f"Đã ghi {tong} hàng trong {len(du_lieu)} bảng vào '{duong_dan}'.")
    print("Tệp này chứa dữ liệu cá nhân. Giữ như giữ cơ sở dữ liệu.")
    return 0


def phuc_hoi(db, args) -> int:
    """Nạp một tệp sao lưu vào cơ sở dữ liệu đang trỏ tới.

    Xoá sạch rồi nạp lại, nên nó chỉ dùng cho hai việc: diễn tập vào một cơ sở
    dữ liệu trống, và cứu hộ thật sau khi đã mất dữ liệu. Cố ý bắt gõ thêm
    --chac-chan, và cố ý nói rõ đang ghi đè lên đâu trước khi làm gì.
    """
    duong_dan = Path(args.tep)
    if not duong_dan.exists():
        print(f"Không tìm thấy '{duong_dan}'.")
        return 1

    goi = json.loads(duong_dan.read_text(encoding="utf-8"))
    if goi.get("phien_ban") != PHIEN_BAN_SAO_LUU:
        print(f"Tệp sao lưu phiên bản {goi.get('phien_ban')}, mã này đọc "
              f"phiên bản {PHIEN_BAN_SAO_LUU}.")
        return 1

    from app.config import DATABASE_URL

    co_san = set(inspect(engine).get_table_names())
    dang_co = sum(
        len(db.execute(bang.select()).fetchall())
        for bang in _thu_tu_bang()
        if bang.name in co_san
    )
    if not args.chac_chan:
        print(f"Sẽ XOÁ SẠCH {dang_co} hàng đang có tại:")
        print(f"  {DATABASE_URL}")
        print(f"rồi nạp lại từ '{duong_dan}'.")
        print("Thêm --chac-chan nếu đúng ý bạn.")
        return 1

    Base.metadata.create_all(bind=engine)

    # Xoá theo thứ tự ngược: con trước, cha sau.
    for bang in reversed(_thu_tu_bang()):
        db.execute(bang.delete())

    tong = 0
    for bang in _thu_tu_bang():
        rows = goi["bang"].get(bang.name, [])
        if not rows:
            continue
        # Chỉ nạp những cột lược đồ hiện tại còn có: tệp sao lưu cũ hơn một lần
        # di trú thì thiếu cột mới, và cột bỏ đi thì thừa. Cả hai nên bỏ qua
        # lặng lẽ chứ không nên làm hỏng cả lần phục hồi.
        cot = set(bang.columns.keys())
        db.execute(
            bang.insert(),
            [{k: _doc_lai(v) for k, v in row.items() if k in cot} for row in rows],
        )
        tong += len(rows)

    db.commit()
    print(f"Đã nạp {tong} hàng từ '{duong_dan}'.")
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

    p = sub.add_parser("doi-email", help="Đổi địa chỉ thư của một tài khoản")
    p.add_argument("email_cu")
    p.add_argument("email_moi")
    p.set_defaults(func=doi_email)

    p = sub.add_parser("xoa-cho", help="Các yêu cầu xoá đang chờ")
    p.set_defaults(func=xoa_cho)

    p = sub.add_parser("xoa", help="Xoá vĩnh viễn một tài khoản")
    p.add_argument("email")
    p.add_argument("--chac-chan", action="store_true", dest="chac_chan")
    p.set_defaults(func=xoa)

    p = sub.add_parser("sao-luu", help="Đổ cả cơ sở dữ liệu ra một tệp JSON")
    p.add_argument("tep")
    p.add_argument("--ghi-de", action="store_true", dest="ghi_de")
    p.set_defaults(func=sao_luu)

    p = sub.add_parser("phuc-hoi", help="Nạp lại từ tệp sao lưu (XOÁ SẠCH trước)")
    p.add_argument("tep")
    p.add_argument("--chac-chan", action="store_true", dest="chac_chan")
    p.set_defaults(func=phuc_hoi)

    args = parser.parse_args(argv)
    db = SessionLocal()
    try:
        return args.func(db, args)
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
