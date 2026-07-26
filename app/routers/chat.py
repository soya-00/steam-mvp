"""Hai chế độ trò chuyện với AI.

Khung màn hình và luồng dữ liệu dựng ở Giai đoạn 2; phần gọi Gemini thật nằm
ở Giai đoạn 4. Chế độ có cấu trúc (Không gian tư duy) nằm trong student.py vì
nó đi theo kịch bản beat; đây là chế độ tự do.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db import get_db
from app.models import JournalEntry, User
from app.templating import templates

router = APIRouter()


@router.get("/ho-so/y-tuong-tu-do", response_class=HTMLResponse)
def freeform(
    request: Request,
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user is None:
        return RedirectResponse("/dang-nhap", status_code=303)
    if user.is_teacher:
        return RedirectResponse("/giao-vien", status_code=303)

    ideas = (
        db.query(JournalEntry)
        .filter(JournalEntry.student_id == user.id, JournalEntry.source == "freeform")
        .order_by(JournalEntry.created_at.desc())
        .all()
    )

    return templates.TemplateResponse(
        request,
        "student/y_tuong_tu_do.html",
        {"user": user, "branch": "ho_so", "ideas": ideas},
    )
