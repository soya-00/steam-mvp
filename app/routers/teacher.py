"""Luồng giáo viên — dựng ở Giai đoạn 3."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.auth import get_current_user
from app.models import User
from app.templating import templates

router = APIRouter(prefix="/giao-vien")


@router.get("", response_class=HTMLResponse)
def teacher_home(request: Request, user: User | None = Depends(get_current_user)):
    if user is None:
        return RedirectResponse("/dang-nhap", status_code=303)
    if not user.is_teacher:
        return RedirectResponse("/trang-ca-nhan", status_code=303)
    return templates.TemplateResponse(
        request,
        "teacher/soon.html",
        {"user": user, "branch": "lop"},
    )
