"""Luồng học sinh. Trang cá nhân là điểm hội tụ chính của sơ đồ."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db import get_db
from app.models import (
    Badge,
    ClassMembership,
    Feedback,
    JournalEntry,
    Notification,
    PortfolioEntry,
    User,
)
from app.scenarios import all_scenarios, get_scenario
from app.templating import templates

router = APIRouter()


def require_student(user: User | None = Depends(get_current_user)) -> User | RedirectResponse:
    return user


def _guard(user: User | None):
    """Chưa đăng nhập -> về trang đăng nhập. Giáo viên -> về khu giáo viên."""
    if user is None:
        return RedirectResponse("/dang-nhap", status_code=303)
    if user.is_teacher:
        return RedirectResponse("/giao-vien", status_code=303)
    return None


@router.get("/du-an", response_class=HTMLResponse)
@router.get("/ho-so", response_class=HTMLResponse)
@router.get("/huy-hieu", response_class=HTMLResponse)
@router.get("/tai-nguyen", response_class=HTMLResponse)
def branch_placeholder(request: Request, user: User | None = Depends(get_current_user)):
    """Bốn nhánh — nội dung thật được dựng ở Giai đoạn 2."""
    if (redirect := _guard(user)) is not None:
        return redirect
    branch = {
        "/du-an": ("du_an", "Dự án học tập"),
        "/ho-so": ("ho_so", "Hồ sơ năng lực"),
        "/huy-hieu": ("huy_hieu", "Huy hiệu"),
        "/tai-nguyen": ("tai_nguyen", "Tài nguyên miễn phí"),
    }[request.url.path]
    return templates.TemplateResponse(
        request,
        "student/soon.html",
        {"user": user, "branch": branch[0], "branch_title": branch[1]},
    )


@router.get("/trang-ca-nhan", response_class=HTMLResponse)
def hub(
    request: Request,
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user)) is not None:
        return redirect

    entries = (
        db.query(JournalEntry)
        .filter(JournalEntry.student_id == user.id)
        .order_by(JournalEntry.created_at.desc())
        .all()
    )
    portfolio = (
        db.query(PortfolioEntry).filter(PortfolioEntry.student_id == user.id).all()
    )
    badges = db.query(Badge).filter(Badge.student_id == user.id).all()
    memberships = (
        db.query(ClassMembership).filter(ClassMembership.student_id == user.id).all()
    )
    class_ids = [m.class_id for m in memberships]

    feedback = (
        db.query(Feedback)
        .filter(Feedback.student_id == user.id)
        .order_by(Feedback.created_at.desc())
        .all()
    )

    notifications = (
        db.query(Notification)
        .filter(
            (Notification.class_id.in_(class_ids) if class_ids else False)
            | (Notification.student_id == user.id)
            | ((Notification.class_id.is_(None)) & (Notification.student_id.is_(None)))
        )
        .order_by(Notification.created_at.desc())
        .limit(3)
        .all()
    )

    fields_touched = {
        s.field
        for e in entries
        if e.scenario_id and (s := get_scenario(e.scenario_id)) is not None
    }

    return templates.TemplateResponse(
        request,
        "student/hub.html",
        {
            "user": user,
            "branch": None,
            "entries": entries[:4],
            "entry_count": len(entries),
            "portfolio_count": len(portfolio),
            "shared_count": sum(1 for p in portfolio if p.shared),
            "badges": badges,
            "classes": [m.klass for m in memberships],
            "feedback": feedback,
            "notifications": notifications,
            "fields_touched": fields_touched,
            "scenarios": all_scenarios(),
        },
    )
