from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app import progress as progress_of
from app.accounts import clean_name, message_for
from app.auth import get_current_user
from app.config import FIELD_NAME_BY_KEY, STEAM_FIELDS
from app.db import get_db
from app.models import (
    Assignment,
    Badge,
    Class,
    ClassMembership,
    Feedback,
    GuidedSession,
    JournalEntry,
    Notification,
    PortfolioEntry,
    User,
)
from app.lop import doi_ma, doi_ten, dong_lop, go_khoi_lop, mo_lai_lop, tao_lop
from app.scenarios import all_scenarios, get_scenario
from app.templating import templates

router = APIRouter(prefix="/giao-vien")


def _guard(user: User | None, request: Request | None = None):
    """Cửa duy nhất dẫn vào toàn bộ /giao-vien.

    Tài khoản bị đình chỉ nhận một trang 403 chứ không phải chuyển hướng: bên
    học sinh đá giáo viên sang /giao-vien, nên chuyển hướng ngược lại
    /trang-ca-nhan sẽ thành vòng lặp vô tận.
    """
    if user is None:
        return RedirectResponse("/dang-nhap", status_code=303)
    if not user.is_teacher:
        return RedirectResponse("/trang-ca-nhan", status_code=303)
    if not user.can_teach:
        return templates.TemplateResponse(
            request,
            "teacher/tam_khoa.html",
            {"user": user, "focus": True},
            status_code=403,
        )
    return None


def _class_or_none(db: Session, class_id: int, teacher: User) -> Class | None:
    """Nạp sẵn học sinh: trang lớp đọc `klass.students` ngay, và để lười thì
    mỗi em là một câu truy vấn nữa."""
    return (
        db.query(Class)
        .filter(Class.id == class_id, Class.teacher_id == teacher.id)
        .options(selectinload(Class.memberships).selectinload(ClassMembership.student))
        .first()
    )


def _my_class_ids(db: Session, teacher: User) -> list[int]:
    """Số hiệu các lớp của chính giáo viên này.

    Bốn chỗ trong file này từng viết lại cùng một câu truy vấn để trả lời "em
    này có phải học sinh của tôi không". Một bản sao viết sai là một giáo viên
    đọc được bài của lớp người khác, nên câu đó chỉ nên tồn tại một lần.
    """
    return [row[0] for row in db.query(Class.id).filter(Class.teacher_id == teacher.id).all()]


def _taught_student(db: Session, teacher: User, student_id: int) -> ClassMembership | None:
    ids = _my_class_ids(db, teacher)
    if not ids:
        return None
    return (
        db.query(ClassMembership)
        .filter(
            ClassMembership.student_id == student_id,
            ClassMembership.class_id.in_(ids),
        )
        .first()
    )


def _ten_lop_hop_le(raw: str) -> tuple[str | None, str | None]:
    """Tên lớp hiện trên màn hình học sinh, nên đi qua đúng bộ lọc như tên
    người. Trả về (tên, mã lỗi) — một trong hai luôn là None."""
    return clean_name(raw)


def _tom_tat(student: User, entries: list[JournalEntry], badge_count: int) -> dict:
    return {
        "student": student,
        "entries": entries,
        "entry_count": len(entries),
        "submitted": sum(1 for e in entries if e.submitted),
        "badge_count": badge_count,
        "last_active": entries[0].created_at if entries else None,
    }


def _student_summary(db: Session, student: User) -> dict:
    """Tóm tắt cho đúng một em. Dùng ở trang chi tiết học sinh, nơi chỉ có một."""
    entries = (
        db.query(JournalEntry)
        .filter(JournalEntry.student_id == student.id)
        .order_by(JournalEntry.created_at.desc())
        .all()
    )
    badges = db.query(Badge).filter(Badge.student_id == student.id).count()
    return _tom_tat(student, entries, badges)


def _summaries_for(db: Session, students: list[User]) -> list[dict]:
    """Tóm tắt cho cả lớp trong hai câu truy vấn, không phải hai câu mỗi em.

    Bản cũ gọi `_student_summary` trong vòng lặp, tức 2N câu. Ở lớp 30 em không
    ai để ý; ở một trường 300 em thì trang không mở nổi. `tests/test_tien_do.py`
    giữ trần cho trang này.
    """
    if not students:
        return []

    ids = [s.id for s in students]

    entries_by_student: dict[int, list[JournalEntry]] = {}
    for entry in (
        db.query(JournalEntry)
        .filter(JournalEntry.student_id.in_(ids))
        .order_by(JournalEntry.created_at.desc())
        .all()
    ):
        entries_by_student.setdefault(entry.student_id, []).append(entry)

    badges_by_student: dict[int, int] = {}
    for student_id, so_luong in (
        db.query(Badge.student_id, func.count(Badge.id))
        .filter(Badge.student_id.in_(ids))
        .group_by(Badge.student_id)
        .all()
    ):
        badges_by_student[student_id] = so_luong

    return [
        _tom_tat(s, entries_by_student.get(s.id, []), badges_by_student.get(s.id, 0))
        for s in students
    ]


@router.get("", response_class=HTMLResponse)
def teacher_home(
    request: Request,
    loi: str = "",
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user, request)) is not None:
        return redirect

    classes = _my_classes(db, user, gom_da_dong=True)
    rows, da_dong = [], []
    for klass in classes:
        students = klass.students
        ids = [s.id for s in students]
        entry_count = (
            db.query(JournalEntry).filter(JournalEntry.student_id.in_(ids)).count()
            if ids
            else 0
        )
        (da_dong if klass.da_dong else rows).append(
            {
                "klass": klass,
                "student_count": len(students),
                "entry_count": entry_count,
                "assignment_count": len(klass.assignments),
            }
        )

    return templates.TemplateResponse(
        request,
        "teacher/home.html",
        {
            "user": user,
            "branch": "lop",
            "rows": rows,
            "da_dong": da_dong,
            "loi": message_for(loi),
        },
    )


@router.post("/lop/tao")
def create_class(
    request: Request,
    ten_lop: str = Form(""),
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user, request)) is not None:
        return redirect

    name, problem = _ten_lop_hop_le(ten_lop)
    if problem == "ten_trong":
        name, problem = "Lớp chưa đặt tên", None
    if problem:
        return RedirectResponse(f"/giao-vien?loi={problem}#tao-lop", status_code=303)

    klass = tao_lop(db, user, name)
    return RedirectResponse(f"/giao-vien/lop/{klass.id}", status_code=303)


@router.get("/lop/{class_id}", response_class=HTMLResponse)
def class_detail(
    request: Request,
    class_id: int,
    loi: str = "",
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user, request)) is not None:
        return redirect

    klass = _class_or_none(db, class_id, user)
    if klass is None:
        return RedirectResponse("/giao-vien", status_code=303)

    summaries = _summaries_for(db, klass.students)
    summaries.sort(key=lambda s: s["student"].name)

    return templates.TemplateResponse(
        request,
        "teacher/lop.html",
        {
            "user": user,
            "branch": "lop",
            "klass": klass,
            "summaries": summaries,
            "loi": message_for(loi),
            "assignments": sorted(
                klass.assignments, key=lambda a: a.created_at, reverse=True
            ),
            "scenarios": all_scenarios(),
            "scenario_of": {a.id: get_scenario(a.scenario_id) for a in klass.assignments},
        },
    )


@router.post("/lop/{class_id}/giao")
def assign_work(
    request: Request,
    class_id: int,
    muc_tieu: str = Form(""),
    hinh_thuc: str = Form("online"),
    ghi_chu: str = Form(""),
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user, request)) is not None:
        return redirect

    klass = _class_or_none(db, class_id, user)
    if klass is None:
        return RedirectResponse("/giao-vien", status_code=303)
    if klass.da_dong:
        # Đóng lớp là ngừng nhận việc mới, không phải ẩn lớp đi. Nhiệm vụ cũ
        # vẫn đọc được; chỉ không giao thêm được nữa.
        return RedirectResponse(f"/giao-vien/lop/{class_id}?loi=lop_da_dong", status_code=303)

    scenario_id = field = None
    if muc_tieu.startswith("kich-huong:"):
        candidate = muc_tieu.split(":", 1)[1]
        if get_scenario(candidate):
            scenario_id = candidate
    elif muc_tieu.startswith("linh-vuc:"):
        field = FIELD_NAME_BY_KEY.get(muc_tieu.split(":", 1)[1])

    if scenario_id is None and field is None:
        return RedirectResponse(f"/giao-vien/lop/{class_id}", status_code=303)

    db.add(
        Assignment(
            class_id=klass.id,
            scenario_id=scenario_id,
            field=field,
            mode="offline" if hinh_thuc == "offline" else "online",
            note=ghi_chu.strip(),
        )
    )
    db.commit()
    return RedirectResponse(f"/giao-vien/lop/{class_id}", status_code=303)


@router.post("/lop/{class_id}/sua")
def rename_class(
    request: Request,
    class_id: int,
    ten_lop: str = Form(""),
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user, request)) is not None:
        return redirect

    klass = _class_or_none(db, class_id, user)
    if klass is None:
        return RedirectResponse("/giao-vien", status_code=303)

    name, problem = _ten_lop_hop_le(ten_lop)
    if problem:
        return RedirectResponse(
            f"/giao-vien/lop/{class_id}?loi={problem}#quan-ly", status_code=303
        )

    doi_ten(db, klass, name)
    return RedirectResponse(f"/giao-vien/lop/{class_id}#quan-ly", status_code=303)


@router.post("/lop/{class_id}/doi-ma")
def rotate_class_code(
    request: Request,
    class_id: int,
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cấp mã mới khi mã cũ bị chụp màn hình hoặc chuyền ra ngoài.

    Không đụng tới danh sách lớp: những em đã vào vẫn ở trong lớp, và mã ẩn
    danh trong bản tải về cũng không đổi — nó bám vào `roster_prefix`, đóng
    băng từ lúc tạo lớp.
    """
    if (redirect := _guard(user, request)) is not None:
        return redirect

    klass = _class_or_none(db, class_id, user)
    if klass is None:
        return RedirectResponse("/giao-vien", status_code=303)

    doi_ma(db, klass)
    return RedirectResponse(f"/giao-vien/lop/{class_id}#quan-ly", status_code=303)


@router.post("/lop/{class_id}/dong")
def close_class(
    request: Request,
    class_id: int,
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Kết thúc lớp: không nhận thêm ai, mã hết tác dụng, bài cũ vẫn đọc được.

    Cố ý không có xoá lớp. Trong một đợt thử nghiệm không nên có nút nào huỷ
    được dữ liệu thật, và đóng lớp thì mở lại được bằng đúng một lần bấm.
    """
    if (redirect := _guard(user, request)) is not None:
        return redirect

    klass = _class_or_none(db, class_id, user)
    if klass is None:
        return RedirectResponse("/giao-vien", status_code=303)

    dong_lop(db, klass)
    return RedirectResponse(f"/giao-vien/lop/{class_id}#quan-ly", status_code=303)


@router.post("/lop/{class_id}/mo-lai")
def reopen_class(
    request: Request,
    class_id: int,
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user, request)) is not None:
        return redirect

    klass = _class_or_none(db, class_id, user)
    if klass is None:
        return RedirectResponse("/giao-vien", status_code=303)

    mo_lai_lop(db, klass)
    return RedirectResponse(f"/giao-vien/lop/{class_id}#quan-ly", status_code=303)


@router.post("/lop/{class_id}/go/{student_id}")
def remove_student(
    request: Request,
    class_id: int,
    student_id: int,
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Gỡ một em khỏi lớp — vào nhầm lớp là chuyện xảy ra hằng tuần.

    Chỉ xoá tư cách thành viên. Bài viết, hồ sơ và huy hiệu của em vẫn nguyên,
    và em vào lại được bằng mã lớp, nên đây không phải một thao tác huỷ dữ
    liệu.
    """
    if (redirect := _guard(user, request)) is not None:
        return redirect

    klass = _class_or_none(db, class_id, user)
    if klass is None:
        return RedirectResponse("/giao-vien", status_code=303)

    go_khoi_lop(db, class_id, student_id)
    return RedirectResponse(f"/giao-vien/lop/{class_id}", status_code=303)


@router.get("/hoc-sinh/{student_id}", response_class=HTMLResponse)
def student_detail(
    request: Request,
    student_id: int,
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user, request)) is not None:
        return redirect

    membership = _taught_student(db, user, student_id)
    if membership is None:
        return RedirectResponse("/giao-vien", status_code=303)

    student = db.get(User, student_id)
    summary = _student_summary(db, student)
    portfolio = (
        db.query(PortfolioEntry)
        .filter(PortfolioEntry.student_id == student_id)
        .order_by(PortfolioEntry.order_index)
        .all()
    )
    notes = (
        db.query(Feedback)
        .filter(Feedback.student_id == student_id, Feedback.teacher_id == user.id)
        .order_by(Feedback.created_at.desc())
        .all()
    )
    badges = db.query(Badge).filter(Badge.student_id == student_id).all()

    return templates.TemplateResponse(
        request,
        "teacher/hoc_sinh.html",
        {
            "user": user,
            "branch": "lop",
            "student": student,
            "klass": membership.klass,
            "summary": summary,
            "portfolio": portfolio,
            "notes": notes,
            "badges": badges,
            "scenario_of": {
                e.id: get_scenario(e.scenario_id) for e in summary["entries"]
            },
        },
    )


@router.post("/hoc-sinh/{student_id}/nhan-xet")
def leave_feedback(
    request: Request,
    student_id: int,
    noi_dung: str = Form(""),
    journal_entry_id: str = Form(""),
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user, request)) is not None:
        return redirect

    content = noi_dung.strip()
    if not content:
        return RedirectResponse(f"/giao-vien/hoc-sinh/{student_id}", status_code=303)

    if _taught_student(db, user, student_id) is None:
        return RedirectResponse("/giao-vien", status_code=303)

    entry_id = None
    if journal_entry_id.isdigit():
        entry = db.get(JournalEntry, int(journal_entry_id))
        if entry is not None and entry.student_id == student_id:
            entry_id = entry.id

    db.add(
        Feedback(
            teacher_id=user.id,
            student_id=student_id,
            journal_entry_id=entry_id,
            content=content,
        )
    )
    db.commit()
    return RedirectResponse(f"/giao-vien/hoc-sinh/{student_id}", status_code=303)


@router.get("/huong-dan", response_class=HTMLResponse)
def teacher_guide(
    request: Request,
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user, request)) is not None:
        return redirect
    return templates.TemplateResponse(
        request,
        "teacher/huong_dan.html",
        {"user": user, "branch": "lop"},
    )


@router.get("/ma-lop", response_class=HTMLResponse)
def class_codes(
    request: Request,
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user, request)) is not None:
        return redirect

    # Lớp đã đóng không lên bảng mã: mã của nó không nhận thêm ai, nên đọc nó
    # cho học sinh chỉ tạo ra một lần thử vào lớp thất bại.
    classes = _my_classes(db, user)
    return templates.TemplateResponse(
        request,
        "teacher/ma_lop.html",
        {
            "user": user,
            "branch": "lop",
            "rows": [{"klass": c, "student_count": len(c.students)} for c in classes],
        },
    )


def _my_classes(db: Session, teacher: User, gom_da_dong: bool = False) -> list[Class]:
    """Nạp sẵn danh sách học sinh: nếu để lười, mỗi em là một câu truy vấn và
    một trường 200 em sẽ ngốn hàng trăm câu cho mỗi lần mở trang.

    Mặc định bỏ qua lớp đã đóng. Đóng lớp là xếp lại chứ không phải xoá, nên
    lớp cũ vẫn mở đọc được — chỉ là nó không còn chen vào danh sách lớp đang
    dạy, bảng mã lớp hay bộ lọc tiến độ nữa.
    """
    q = db.query(Class).filter(Class.teacher_id == teacher.id)
    if not gom_da_dong:
        q = q.filter(Class.dong_luc.is_(None))
    return (
        q.options(selectinload(Class.memberships).selectinload(ClassMembership.student))
        .order_by(Class.name)
        .all()
    )


def _scope(db: Session, teacher: User, lop: str) -> tuple[list[Class], Class | None, list[Class]]:
    classes = _my_classes(db, teacher)
    selected = None
    if lop.isdigit():
        # Chỉ chọn được trong số lớp của chính mình — id lạ thì rơi về tất cả.
        selected = next((c for c in classes if c.id == int(lop)), None)
    return ([selected] if selected else classes), selected, classes


def _sessions_for(db: Session, classes: list[Class]) -> dict[tuple[int, str], GuidedSession]:
    ids = [s.id for klass in classes for s in klass.students]
    if not ids:
        return {}
    return {
        (gs.student_id, gs.scenario_id): gs
        for gs in db.query(GuidedSession).filter(GuidedSession.student_id.in_(ids)).all()
    }


def _tally(classes: list[Class], sessions: dict, scenario) -> dict:
    counts = {"chua_bat_dau": 0, "dang_lam": 0, "da_xong": 0}
    for klass in classes:
        for student in klass.students:
            gs = sessions.get((student.id, scenario.id))
            counts[progress_of.status(gs)] += 1
    counts["tong"] = sum(counts[k] for k in ("chua_bat_dau", "dang_lam", "da_xong"))
    return counts


@router.get("/tien-do", response_class=HTMLResponse)
def progress_fields(
    request: Request,
    lop: str = "",
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user, request)) is not None:
        return redirect

    classes, selected, all_classes = _scope(db, user, lop)
    sessions = _sessions_for(db, classes)
    assignments = [a for klass in classes for a in klass.assignments]

    rows = []
    for field in STEAM_FIELDS:
        pool = [s for s in all_scenarios() if s.field == field["name"]]
        assigned = 0
        for a in assignments:
            if a.field == field["name"]:
                assigned += 1
            elif a.scenario_id and (sc := get_scenario(a.scenario_id)) and sc.field == field["name"]:
                assigned += 1

        active = finished = 0
        for scenario in pool:
            tally = _tally(classes, sessions, scenario)
            active += tally["dang_lam"]
            finished += tally["da_xong"]

        rows.append(
            {
                "field": field,
                "scenario_count": len(pool),
                "assigned": assigned,
                "active": active,
                "finished": finished,
            }
        )

    return templates.TemplateResponse(
        request,
        "teacher/tien_do.html",
        {
            "user": user,
            "branch": "tien_do",
            "rows": rows,
            "all_classes": all_classes,
            "selected": selected,
        },
    )


@router.get("/tien-do/{field_key}", response_class=HTMLResponse)
def progress_field(
    request: Request,
    field_key: str,
    lop: str = "",
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user, request)) is not None:
        return redirect

    field_name = FIELD_NAME_BY_KEY.get(field_key)
    if field_name is None:
        return RedirectResponse("/giao-vien/tien-do", status_code=303)

    classes, selected, all_classes = _scope(db, user, lop)
    sessions = _sessions_for(db, classes)
    pool = [s for s in all_scenarios() if s.field == field_name]

    cards, covered = [], set()
    for klass in classes:
        for a in sorted(klass.assignments, key=lambda x: x.created_at, reverse=True):
            if a.field == field_name:
                targets = pool
            elif a.scenario_id and (sc := get_scenario(a.scenario_id)) and sc.field == field_name:
                targets = [sc]
            else:
                continue
            covered.update(s.id for s in targets)
            cards.append(
                {
                    "assignment": a,
                    "klass": klass,
                    "whole_field": a.field == field_name,
                    "targets": [
                        {"scenario": s, "tally": _tally([klass], sessions, s)} for s in targets
                    ],
                }
            )

    loose = []
    for scenario in pool:
        if scenario.id in covered:
            continue
        tally = _tally(classes, sessions, scenario)
        if tally["dang_lam"] or tally["da_xong"]:
            loose.append({"scenario": scenario, "tally": tally})

    return templates.TemplateResponse(
        request,
        "teacher/tien_do_linh_vuc.html",
        {
            "user": user,
            "branch": "tien_do",
            "field_key": field_key,
            "field_name": field_name,
            "cards": cards,
            "loose": loose,
            "all_classes": all_classes,
            "selected": selected,
        },
    )


@router.get("/tien-do/{field_key}/{scenario_id}", response_class=HTMLResponse)
def progress_scenario(
    request: Request,
    field_key: str,
    scenario_id: str,
    lop: str = "",
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user, request)) is not None:
        return redirect

    scenario = get_scenario(scenario_id)
    if scenario is None or FIELD_NAME_BY_KEY.get(field_key) != scenario.field:
        return RedirectResponse("/giao-vien/tien-do", status_code=303)

    classes, selected, all_classes = _scope(db, user, lop)
    sessions = _sessions_for(db, classes)

    rows = []
    for klass in classes:
        for student in klass.students:
            gs = sessions.get((student.id, scenario.id))
            rows.append(
                {
                    "student": student,
                    "klass": klass,
                    "summary": progress_of.summary(scenario, gs),
                }
            )
    rows.sort(key=lambda r: r["student"].name)

    counts = {"chua_bat_dau": 0, "dang_lam": 0, "da_xong": 0}
    for row in rows:
        counts[row["summary"]["status"]] += 1

    return templates.TemplateResponse(
        request,
        "teacher/tien_do_tinh_huong.html",
        {
            "user": user,
            "branch": "tien_do",
            "field_key": field_key,
            "scenario": scenario,
            "rows": rows,
            "counts": counts,
            "status_labels": progress_of.STATUS_LABELS,
            "all_classes": all_classes,
            "selected": selected,
        },
    )


@router.get("/tai-lieu", response_class=HTMLResponse)
def materials_index(
    request: Request,
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user, request)) is not None:
        return redirect
    return templates.TemplateResponse(
        request,
        "teacher/tai_lieu.html",
        {"user": user, "branch": "tai_lieu", "scenarios": all_scenarios()},
    )


@router.get("/tai-lieu/{scenario_id}", response_class=HTMLResponse)
def printable_materials(
    request: Request,
    scenario_id: str,
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user, request)) is not None:
        return redirect

    scenario = get_scenario(scenario_id)
    if scenario is None:
        return RedirectResponse("/giao-vien", status_code=303)

    return templates.TemplateResponse(
        request,
        "teacher/tai_lieu_in.html",
        {"user": user, "branch": "lop", "scenario": scenario, "printable": True},
    )


@router.get("/thong-bao", response_class=HTMLResponse)
def notifications_view(
    request: Request,
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user, request)) is not None:
        return redirect

    classes = db.query(Class).filter(Class.teacher_id == user.id).all()
    class_ids = [c.id for c in classes]
    sent = (
        db.query(Notification)
        .filter(Notification.class_id.in_(class_ids))
        .order_by(Notification.created_at.desc())
        .all()
        if class_ids
        else []
    )
    platform = (
        db.query(Notification)
        .filter(Notification.class_id.is_(None), Notification.student_id.is_(None))
        .order_by(Notification.created_at.desc())
        .all()
    )

    return templates.TemplateResponse(
        request,
        "teacher/thong_bao.html",
        {
            "user": user,
            "branch": "thong_bao",
            "classes": classes,
            "sent": sent,
            "platform": platform,
            "class_of": {c.id: c for c in classes},
        },
    )


@router.post("/thong-bao")
def send_notification(
    request: Request,
    lop: str = Form(""),
    loai: str = Form("workshop"),
    tieu_de: str = Form(""),
    noi_dung: str = Form(""),
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user, request)) is not None:
        return redirect

    title = tieu_de.strip()
    if not title or not lop.isdigit():
        return RedirectResponse("/giao-vien/thong-bao", status_code=303)

    klass = _class_or_none(db, int(lop), user)
    if klass is None:
        return RedirectResponse("/giao-vien/thong-bao", status_code=303)

    db.add(
        Notification(
            class_id=klass.id,
            type="talkshow" if loai == "talkshow" else "workshop",
            title=title,
            content=noi_dung.strip(),
        )
    )
    db.commit()
    return RedirectResponse("/giao-vien/thong-bao", status_code=303)
