"""Ý tưởng tự do — chế độ trò chuyện không có khung sườn.

Chế độ có cấu trúc (Không gian tư duy) nằm trong student.py vì nó đi theo kịch
bản beat của từng kịch huống. Ở đây học sinh dẫn dắt cuộc trò chuyện.

Điểm mấu chốt: khi trợ lý nhận ra một ý đáng giữ, nó chỉ hiện nút hỏi ý học
sinh. Không có gì được thêm vào hồ sơ nếu em không tự bấm.
"""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from itsdangerous import URLSafeSerializer
from sqlalchemy.orm import Session

from app.auth import get_current_user, session_key
from app.config import SECRET_KEY
from app.db import get_db
from app.gemini import freeform_reply, quota_left
from app.models import JournalEntry, PortfolioEntry, User
from app.templating import templates

router = APIRouter()

# Lịch sử hội thoại sống trong cookie đã ký — không cần bảng riêng cho bản mẫu,
# và tự biến mất khi đóng phiên, đúng tinh thần "không lưu thứ em chưa đồng ý".
_history = URLSafeSerializer(SECRET_KEY, salt="gals-brainstorm")
HISTORY_COOKIE = "gals_bs"
MAX_TURNS = 24


def _guard(user: User | None):
    if user is None:
        return RedirectResponse("/dang-nhap", status_code=303)
    if user.is_teacher:
        return RedirectResponse("/giao-vien", status_code=303)
    return None


def _load_history(request: Request) -> list[dict]:
    raw = request.cookies.get(HISTORY_COOKIE)
    if not raw:
        return []
    try:
        data = _history.loads(raw)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _store_history(response, history: list[dict]) -> None:
    trimmed = history[-MAX_TURNS:]
    response.set_cookie(
        HISTORY_COOKIE,
        _history.dumps(trimmed),
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 6,
    )


def _ideas(db: Session, user: User) -> list[JournalEntry]:
    return (
        db.query(JournalEntry)
        .filter(JournalEntry.student_id == user.id, JournalEntry.source == "freeform")
        .order_by(JournalEntry.created_at.desc())
        .all()
    )


@router.get("/ho-so/y-tuong-tu-do", response_class=HTMLResponse)
def freeform_page(
    request: Request,
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user)) is not None:
        return redirect

    return templates.TemplateResponse(
        request,
        "student/y_tuong_tu_do.html",
        {
            "user": user,
            "branch": "ho_so",
            "history": _load_history(request),
            "ideas": _ideas(db, user),
            "quota": quota_left(session_key(request)),
        },
    )


@router.post("/ho-so/y-tuong-tu-do", response_class=HTMLResponse)
def freeform_send(
    request: Request,
    tin_nhan: str = Form(""),
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """HTMX gửi tin nhắn và nhận về khung hội thoại đã cập nhật."""
    if (redirect := _guard(user)) is not None:
        return redirect

    message = tin_nhan.strip()
    history = _load_history(request)

    if message:
        reply, idea = freeform_reply(history, message, session_key(request))
        history.append({"role": "user", "text": message})
        history.append({"role": "ai", "text": reply, "idea": idea})

    response = templates.TemplateResponse(
        request,
        "student/partials/brainstorm.html",
        {
            "user": user,
            "history": history,
            "quota": quota_left(session_key(request)),
        },
    )
    _store_history(response, history)
    return response


@router.post("/ho-so/y-tuong-tu-do/giu", response_class=HTMLResponse)
def keep_idea(
    request: Request,
    y_tuong: str = Form(""),
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Học sinh bấm đồng ý -> tạo mục nháp trong hồ sơ.

    Mục này vẫn `shared=False`; muốn công khai thì phải bấm chia sẻ ở Hồ sơ
    năng lực. Hai lần xác nhận, không lần nào do AI tự quyết.
    """
    if (redirect := _guard(user)) is not None:
        return redirect

    idea = y_tuong.strip()
    if not idea:
        return RedirectResponse("/ho-so/y-tuong-tu-do", status_code=303)

    entry = JournalEntry(
        student_id=user.id,
        source="freeform",
        title=idea[:200],
        content=idea,
        ai_transcript=json.dumps(_load_history(request), ensure_ascii=False),
    )
    db.add(entry)
    db.flush()

    count = db.query(PortfolioEntry).filter(PortfolioEntry.student_id == user.id).count()
    db.add(
        PortfolioEntry(
            student_id=user.id,
            journal_entry_id=entry.id,
            category="ca_hai",
            description=idea,
            order_index=count,
            shared=False,
        )
    )
    db.commit()

    return templates.TemplateResponse(
        request,
        "student/partials/idea_saved.html",
        {"user": user, "idea": idea},
    )


@router.post("/ho-so/y-tuong-tu-do/xoa-lich-su")
def clear_history(request: Request, user: User | None = Depends(get_current_user)):
    if (redirect := _guard(user)) is not None:
        return redirect
    response = RedirectResponse("/ho-so/y-tuong-tu-do", status_code=303)
    response.delete_cookie(HISTORY_COOKIE)
    return response
