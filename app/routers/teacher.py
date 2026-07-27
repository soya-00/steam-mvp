from __future__ import annotations

import random
import string

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.config import FIELD_NAME_BY_KEY, STEAM_FIELDS
from app.db import get_db
from app.models import (
    Assignment,
    Badge,
    Class,
    ClassMembership,
    Feedback,
    JournalEntry,
    Notification,
    PortfolioEntry,
    User,
)
from app.scenarios import all_scenarios, get_scenario
from app.templating import templates

router = APIRouter(prefix="/giao-vien")


def _guard(user: User | None):
    if user is None:
        return RedirectResponse("/dang-nhap", status_code=303)
    if not user.is_teacher:
        return RedirectResponse("/trang-ca-nhan", status_code=303)
    return None


def _new_class_code(db: Session) -> str:
    alphabet = string.ascii_uppercase + string.digits
    for _ in range(50):
        code = "GALS-" + "".join(random.choice(alphabet) for _ in range(4))
        if not db.query(Class).filter(Class.class_code == code).first():
            return code
    return "GALS-" + "".join(random.choice(alphabet) for _ in range(6))


def _class_or_none(db: Session, class_id: int, teacher: User) -> Class | None:
    return (
        db.query(Class)
        .filter(Class.id == class_id, Class.teacher_id == teacher.id)
        .first()
    )


def _student_summary(db: Session, student: User) -> dict:
    entries = (
        db.query(JournalEntry)
        .filter(JournalEntry.student_id == student.id)
        .order_by(JournalEntry.created_at.desc())
        .all()
    )
    return {
        "student": student,
        "entries": entries,
        "entry_count": len(entries),
        "submitted": sum(1 for e in entries if e.submitted),
        "badge_count": db.query(Badge).filter(Badge.student_id == student.id).count(),
        "last_active": entries[0].created_at if entries else None,
    }


@router.get("", response_class=HTMLResponse)
def teacher_home(
    request: Request,
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user)) is not None:
        return redirect

    classes = db.query(Class).filter(Class.teacher_id == user.id).all()
    rows = []
    for klass in classes:
        students = klass.students
        ids = [s.id for s in students]
        entry_count = (
            db.query(JournalEntry).filter(JournalEntry.student_id.in_(ids)).count()
            if ids
            else 0
        )
        rows.append(
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
        {"user": user, "branch": "lop", "rows": rows},
    )


@router.post("/lop/tao")
def create_class(
    ten_lop: str = Form(""),
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user)) is not None:
        return redirect

    name = ten_lop.strip() or "Lớp chưa đặt tên"
    klass = Class(teacher_id=user.id, class_code=_new_class_code(db), name=name)
    db.add(klass)
    db.commit()
    return RedirectResponse(f"/giao-vien/lop/{klass.id}", status_code=303)


@router.get("/lop/{class_id}", response_class=HTMLResponse)
def class_detail(
    request: Request,
    class_id: int,
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user)) is not None:
        return redirect

    klass = _class_or_none(db, class_id, user)
    if klass is None:
        return RedirectResponse("/giao-vien", status_code=303)

    summaries = [_student_summary(db, s) for s in klass.students]
    summaries.sort(key=lambda s: s["student"].name)

    return templates.TemplateResponse(
        request,
        "teacher/lop.html",
        {
            "user": user,
            "branch": "lop",
            "klass": klass,
            "summaries": summaries,
            "assignments": sorted(
                klass.assignments, key=lambda a: a.created_at, reverse=True
            ),
            "scenarios": all_scenarios(),
            "scenario_of": {a.id: get_scenario(a.scenario_id) for a in klass.assignments},
        },
    )


@router.post("/lop/{class_id}/giao")
def assign_work(
    class_id: int,
    muc_tieu: str = Form(""),
    hinh_thuc: str = Form("online"),
    ghi_chu: str = Form(""),
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user)) is not None:
        return redirect

    klass = _class_or_none(db, class_id, user)
    if klass is None:
        return RedirectResponse("/giao-vien", status_code=303)

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


@router.get("/hoc-sinh/{student_id}", response_class=HTMLResponse)
def student_detail(
    request: Request,
    student_id: int,
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user)) is not None:
        return redirect

    my_class_ids = [c.id for c in db.query(Class).filter(Class.teacher_id == user.id).all()]
    membership = (
        db.query(ClassMembership)
        .filter(
            ClassMembership.student_id == student_id,
            ClassMembership.class_id.in_(my_class_ids),
        )
        .first()
        if my_class_ids
        else None
    )
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
    student_id: int,
    noi_dung: str = Form(""),
    journal_entry_id: str = Form(""),
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user)) is not None:
        return redirect

    content = noi_dung.strip()
    if not content:
        return RedirectResponse(f"/giao-vien/hoc-sinh/{student_id}", status_code=303)

    my_class_ids = [c.id for c in db.query(Class).filter(Class.teacher_id == user.id).all()]
    allowed = (
        db.query(ClassMembership)
        .filter(
            ClassMembership.student_id == student_id,
            ClassMembership.class_id.in_(my_class_ids),
        )
        .first()
        if my_class_ids
        else None
    )
    if allowed is None:
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


@router.get("/tai-lieu/{scenario_id}", response_class=HTMLResponse)
def printable_materials(
    request: Request,
    scenario_id: str,
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user)) is not None:
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
    if (redirect := _guard(user)) is not None:
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
    lop: str = Form(""),
    loai: str = Form("workshop"),
    tieu_de: str = Form(""),
    noi_dung: str = Form(""),
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user)) is not None:
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
