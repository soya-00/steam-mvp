from __future__ import annotations

import csv
import io
import json
import zipfile
from datetime import datetime

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy.orm import Session, selectinload

from app import progress as progress_of
from app.auth import get_current_user
from app.db import get_db
from app.models import (
    Assignment,
    Badge,
    Class,
    ClassMembership,
    Feedback,
    GuidedSession,
    JournalEntry,
    PortfolioEntry,
    User,
)
from app.moderation import OK as SCREEN_OK
from app.moderation import REPLIES as SCREEN_REPLIES
from app.moderation import screen
from app.routers.auth import AVATARS, AVATAR_EMOJI
from app.scenarios import get_scenario
from app.templating import templates

router = APIRouter()

MAX_NAME = 60

HUONG_DAN = """GALS — dữ liệu lớp của bạn

Ba tệp trong thư mục này chỉ chứa THÔNG TIN VỀ bài làm, không chứa bài viết
của học sinh. Muốn đọc bài của một em, mở trang của em đó trong ứng dụng.

Học sinh được ghi bằng mã ẩn danh dạng MÃ-LỚP-SỐ. Bảng đối chiếu mã với tên
chỉ hiện trên màn hình trong mục Tải dữ liệu, không nằm trong thư mục này.
Nếu bạn cần bảng đó, hãy tự chép lại và giữ ở nơi an toàn.

nhat-ky.csv   mỗi dòng là một bài của một em: đi tới cấp độ nào, viết bao
              nhiêu câu, hoạt động lần cuối khi nào
phan-hoi.csv  nhận xét do chính bạn viết, đầy đủ nội dung
nhiem-vu.csv  các nhiệm vụ bạn đã giao
"""


def _guard(user: User | None):
    if user is None:
        return RedirectResponse("/dang-nhap", status_code=303)
    return None


def _classes_of(db: Session, user: User) -> list[Class]:
    if user.is_teacher:
        return (
            db.query(Class)
            .filter(Class.teacher_id == user.id)
            .options(selectinload(Class.memberships).selectinload(ClassMembership.student))
            .order_by(Class.name)
            .all()
        )
    return [
        m.klass
        for m in db.query(ClassMembership).filter(ClassMembership.student_id == user.id).all()
    ]


def student_codes(db: Session, klass: Class) -> dict[int, str]:
    """Mã ẩn danh, đánh số theo thứ tự vào lớp nên chỉ thêm vào cuối — cùng một
    em thì lần xuất nào cũng ra cùng một mã."""
    memberships = (
        db.query(ClassMembership)
        .filter(ClassMembership.class_id == klass.id)
        .order_by(ClassMembership.id)
        .all()
    )
    return {
        m.student_id: f"{klass.class_code}-{index:02d}"
        for index, m in enumerate(memberships, start=1)
    }


def _safe_cell(value) -> str:
    """Ô mở đầu bằng = + - @ sẽ được Excel chạy như công thức."""
    text = "" if value is None else str(value)
    return "'" + text if text[:1] in ("=", "+", "-", "@") else text


def _csv_bytes(header: list[str], rows: list[list]) -> bytes:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(header)
    for row in rows:
        writer.writerow([_safe_cell(cell) for cell in row])
    # utf-8-sig: thiếu BOM là Excel hiển thị sai toàn bộ dấu tiếng Việt.
    return buffer.getvalue().encode("utf-8-sig")


def _stamp(value: datetime | None) -> str:
    return value.strftime("%d/%m/%Y %H:%M") if value else ""


@router.get("/tai-khoan", response_class=HTMLResponse)
def account_page(
    request: Request,
    loi: str = "",
    da_luu: str = "",
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user)) is not None:
        return redirect

    classes = _classes_of(db, user)

    shared_items: list[PortfolioEntry] = []
    readers: list[dict] = []
    roster: list[dict] = []

    if user.is_teacher:
        for klass in classes:
            codes = student_codes(db, klass)
            roster.append(
                {
                    "klass": klass,
                    "rows": sorted(
                        (
                            {"code": codes.get(m.student_id, ""), "name": m.student.name}
                            for m in klass.memberships
                        ),
                        key=lambda r: r["code"],
                    ),
                }
            )
    else:
        shared_items = (
            db.query(PortfolioEntry)
            .filter(PortfolioEntry.student_id == user.id)
            .order_by(PortfolioEntry.order_index, PortfolioEntry.created_at)
            .all()
        )
        readers = [{"klass": k, "teacher": k.teacher} for k in classes]

    return templates.TemplateResponse(
        request,
        "account/tai_khoan.html",
        {
            "user": user,
            "branch": None,
            "focus": True,
            "back_href": "/giao-vien" if user.is_teacher else "/trang-ca-nhan",
            "back_label": "Quay lại",
            "avatars": AVATARS,
            "classes": classes,
            "readers": readers,
            "items": shared_items,
            "roster": roster,
            "loi": loi,
            "da_luu": da_luu,
        },
    )


@router.post("/tai-khoan/ten")
def update_name(
    ten: str = Form(""),
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user)) is not None:
        return redirect

    name = " ".join(ten.split())[:MAX_NAME]
    if not name:
        return RedirectResponse("/tai-khoan?loi=Tên không được để trống.#ho-so", status_code=303)

    verdict, _ = screen(name)
    if verdict != SCREEN_OK:
        message = SCREEN_REPLIES.get(verdict, "Tên này chưa dùng được.")
        return RedirectResponse(f"/tai-khoan?loi={message}#ho-so", status_code=303)

    user.name = name
    db.commit()
    return RedirectResponse("/tai-khoan?da_luu=ten#ho-so", status_code=303)


@router.post("/tai-khoan/avatar")
def update_avatar(
    avatar_id: str = Form(""),
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user)) is not None:
        return redirect

    if avatar_id in AVATAR_EMOJI:
        user.avatar_id = avatar_id
        db.commit()
    return RedirectResponse("/tai-khoan?da_luu=avatar#ho-so", status_code=303)


def _student_payload(db: Session, user: User) -> dict:
    entries = (
        db.query(JournalEntry)
        .filter(JournalEntry.student_id == user.id)
        .order_by(JournalEntry.created_at)
        .all()
    )
    sessions = (
        db.query(GuidedSession)
        .filter(GuidedSession.student_id == user.id)
        .order_by(GuidedSession.created_at)
        .all()
    )
    items = (
        db.query(PortfolioEntry)
        .filter(PortfolioEntry.student_id == user.id)
        .order_by(PortfolioEntry.order_index)
        .all()
    )
    badges = db.query(Badge).filter(Badge.student_id == user.id).all()
    notes = (
        db.query(Feedback)
        .filter(Feedback.student_id == user.id)
        .order_by(Feedback.created_at)
        .all()
    )

    return {
        "xuat_luc": datetime.now().isoformat(timespec="seconds"),
        "nguoi_dung": {
            "ten": user.name,
            "vai_tro": "hoc_sinh",
            "avatar": user.avatar_id,
        },
        "lop": [
            {"ten": k.name, "ma_lop": k.class_code, "giao_vien": k.teacher.name}
            for k in _classes_of(db, user)
        ],
        "nhat_ky": [
            {
                "tieu_de": e.title,
                "tinh_huong": e.scenario_id,
                "nguon": e.source,
                "noi_dung": e.content,
                "da_nop": e.submitted,
                "tao_luc": e.created_at.isoformat(timespec="seconds"),
            }
            for e in entries
        ],
        "hanh_trinh": [
            {
                "tinh_huong": gs.scenario_id,
                "da_xong": gs.finished,
                "cau_tra_loi": [
                    {"cap_do": row.get("stage", ""), "cau_hoi": row.get("text", ""),
                     "tra_loi": row.get("answer", "")}
                    for row in progress_of.answered(gs)
                ],
            }
            for gs in sessions
        ],
        "ho_so": [
            {
                "phan_loai": item.category,
                "mo_ta": item.description,
                "dang_chia_se": item.shared,
            }
            for item in items
        ],
        "huy_hieu": [
            {"loai": b.badge_type, "mo_luc": b.earned_at.isoformat(timespec="seconds")}
            for b in badges
        ],
        "loi_nhan_tu_giao_vien": [
            {
                "giao_vien": n.teacher.name,
                "noi_dung": n.content,
                "gui_luc": n.created_at.isoformat(timespec="seconds"),
            }
            for n in notes
        ],
    }


def _teacher_zip(db: Session, user: User) -> bytes:
    classes = _classes_of(db, user)

    journal_rows: list[list] = []
    feedback_rows: list[list] = []
    assignment_rows: list[list] = []

    for klass in classes:
        codes = student_codes(db, klass)
        student_ids = list(codes)

        # Gom theo lớp thay vì hỏi lại cho từng em: một lớp 40 em trước đây
        # tốn hơn 160 câu truy vấn cho riêng phần này.
        sessions_by_student: dict[int, list[GuidedSession]] = {}
        entries_by_student: dict[int, dict[str, JournalEntry]] = {}
        shared_by_student: dict[int, set[str]] = {}
        notes_by_student: dict[int, list[Feedback]] = {}

        if student_ids:
            for gs in db.query(GuidedSession).filter(
                GuidedSession.student_id.in_(student_ids)
            ):
                sessions_by_student.setdefault(gs.student_id, []).append(gs)

            for entry in db.query(JournalEntry).filter(
                JournalEntry.student_id.in_(student_ids)
            ):
                entries_by_student.setdefault(entry.student_id, {})[entry.scenario_id] = entry

            for item in (
                db.query(PortfolioEntry)
                .filter(
                    PortfolioEntry.student_id.in_(student_ids),
                    PortfolioEntry.shared.is_(True),
                )
                .all()
            ):
                if item.journal_entry is not None:
                    shared_by_student.setdefault(item.student_id, set()).add(
                        item.journal_entry.scenario_id
                    )

            for note in (
                db.query(Feedback)
                .filter(
                    Feedback.student_id.in_(student_ids),
                    Feedback.teacher_id == user.id,
                )
                .order_by(Feedback.created_at)
                .all()
            ):
                notes_by_student.setdefault(note.student_id, []).append(note)

        for membership in klass.memberships:
            student = membership.student
            code = codes.get(student.id, "")

            sessions = sessions_by_student.get(student.id, [])
            entry_by_scenario = entries_by_student.get(student.id, {})
            shared_scenarios = shared_by_student.get(student.id, set())

            for gs in sessions:
                scenario = get_scenario(gs.scenario_id)
                if scenario is None:
                    continue
                info = progress_of.summary(scenario, gs)
                entry = entry_by_scenario.get(gs.scenario_id)
                journal_rows.append(
                    [
                        klass.class_code,
                        code,
                        # Tên tình huống, KHÔNG phải entry.title: tiêu đề của
                        # một ghi chép tự do chính là chữ học sinh viết ra.
                        scenario.title,
                        scenario.field,
                        scenario.role,
                        "nhập vai",
                        f"{info['stages_done']}/{info['stage_total']}",
                        "có" if info["finished"] else "không",
                        info["answers"],
                        info["words"],
                        _stamp(gs.created_at),
                        _stamp(info["last_activity"]),
                        "có" if (entry and entry.submitted) else "không",
                        "có" if (entry and entry.image_url) else "không",
                        "có" if (entry and entry.video_url) else "không",
                        "có" if gs.scenario_id in shared_scenarios else "không",
                    ]
                )

            for note in notes_by_student.get(student.id, []):
                target = note.journal_entry
                scenario = get_scenario(target.scenario_id) if target else None
                feedback_rows.append(
                    [
                        klass.class_code,
                        code,
                        scenario.title if scenario else "Nhắn chung",
                        note.content,
                        _stamp(note.created_at),
                    ]
                )

        for assignment in (
            db.query(Assignment)
            .filter(Assignment.class_id == klass.id)
            .order_by(Assignment.created_at)
            .all()
        ):
            scenario = get_scenario(assignment.scenario_id) if assignment.scenario_id else None
            assignment_rows.append(
                [
                    klass.class_code,
                    klass.name,
                    scenario.title if scenario else "",
                    assignment.field or (scenario.field if scenario else ""),
                    "làm ở lớp" if assignment.mode == "offline" else "làm online",
                    assignment.note,
                    _stamp(assignment.created_at),
                ]
            )

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "nhat-ky.csv",
            _csv_bytes(
                [
                    "Mã lớp", "Mã học sinh", "Tình huống", "Lĩnh vực", "Vai",
                    "Kiểu", "Cấp độ đã xong", "Đã đi hết", "Số câu trả lời",
                    "Số từ đã viết", "Bắt đầu", "Hoạt động lần cuối",
                    "Đã nộp", "Có ảnh", "Có video", "Đang chia sẻ công khai",
                ],
                journal_rows,
            ),
        )
        archive.writestr(
            "phan-hoi.csv",
            _csv_bytes(
                ["Mã lớp", "Mã học sinh", "Gắn với tình huống", "Nội dung nhận xét", "Gửi lúc"],
                feedback_rows,
            ),
        )
        archive.writestr(
            "nhiem-vu.csv",
            _csv_bytes(
                ["Mã lớp", "Tên lớp", "Tình huống", "Lĩnh vực", "Hình thức", "Ghi chú", "Giao lúc"],
                assignment_rows,
            ),
        )
        archive.writestr("HUONG-DAN.txt", HUONG_DAN.encode("utf-8"))

    return buffer.getvalue()


@router.get("/tai-khoan/du-lieu")
def export_data(
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user)) is not None:
        return redirect

    today = datetime.now().strftime("%Y-%m-%d")

    if user.is_teacher:
        return Response(
            content=_teacher_zip(db, user),
            media_type="application/zip",
            headers={
                "Content-Disposition": f'attachment; filename="gals-lop-{today}.zip"'
            },
        )

    payload = json.dumps(_student_payload(db, user), ensure_ascii=False, indent=2)
    return Response(
        content=payload.encode("utf-8"),
        media_type="application/json",
        headers={
            "Content-Disposition": f'attachment; filename="gals-cua-toi-{today}.json"'
        },
    )
