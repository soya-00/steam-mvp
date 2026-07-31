from __future__ import annotations

import threading
import time

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.auth import session_key
from app.db import get_db
from app.metrics import REPORT_PREFIX, bump
from app.models import Report
from app.moderation import MAX_INPUT_CHARS
from app.moderation import OK as SCREEN_OK
from app.moderation import screen
from app.templating import templates

router = APIRouter()

MAX_PER_SESSION = 5
WINDOW_SECONDS = 3600
MAX_NOTE_CHARS = 600
MAX_QUOTE_CHARS = 1200

REASONS = {
    "khong_phu_hop": "Nội dung không phù hợp",
    "sai_lech": "Thông tin sai lệch",
    "kho_hieu": "Câu trả lời khó hiểu",
    "khac": "Lý do khác",
}

_lock = threading.Lock()
_sent: dict[str, list[float]] = {}

THANKS = "Cảm ơn bạn đã báo. Mình đã ghi nhận."
THROTTLED = "Bạn vừa gửi khá nhiều báo cáo rồi. Nghỉ một lát rồi quay lại nhé."
REJECTED = "Mình chưa gửi được phần ghi chú này. Bạn viết lại bằng lời bình thường nhé."


def _allow(key: str) -> bool:
    now = time.time()
    with _lock:
        recent = [t for t in _sent.get(key, []) if now - t < WINDOW_SECONDS]
        if len(recent) >= MAX_PER_SESSION:
            _sent[key] = recent
            return False
        recent.append(now)
        _sent[key] = recent
        if len(_sent) > 2000:
            for stale in list(_sent)[:1000]:
                del _sent[stale]
        return True


def _respond(request: Request, message: str, ok: bool) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "partials/phan_hoi_ket_qua.html",
        {"message": message, "ok": ok},
    )


@router.post("/phan-hoi/bao-cao", response_class=HTMLResponse)
def report_reply(
    request: Request,
    ly_do: str = Form("khac"),
    trich_dan: str = Form(""),
    ghi_chu: str = Form(""),
    db: Session = Depends(get_db),
):
    if not _allow(session_key(request)):
        return _respond(request, THROTTLED, False)

    note = (ghi_chu or "").strip()[:MAX_NOTE_CHARS]
    if note:
        verdict, _ = screen(note)
        if verdict != SCREEN_OK:
            return _respond(request, REJECTED, False)

    reason = ly_do if ly_do in REASONS else "khac"
    db.add(
        Report(
            kind="tra_loi_ai",
            reason=reason,
            note=note,
            reported_text=(trich_dan or "").strip()[:MAX_QUOTE_CHARS],
        )
    )
    db.commit()
    bump(f"{REPORT_PREFIX}.tra_loi_ai")
    return _respond(request, THANKS, True)


@router.post("/phan-hoi/gop-y", response_class=HTMLResponse)
def send_feedback(
    request: Request,
    noi_dung: str = Form(""),
    db: Session = Depends(get_db),
):
    if not _allow(session_key(request)):
        return _respond(request, THROTTLED, False)

    body = (noi_dung or "").strip()[:MAX_INPUT_CHARS]
    if not body:
        return _respond(request, "Bạn chưa viết gì cả.", False)

    verdict, _ = screen(body)
    if verdict != SCREEN_OK:
        return _respond(request, REJECTED, False)

    db.add(Report(kind="gop_y", reason="gop_y", note=body[:MAX_NOTE_CHARS]))
    db.commit()
    bump(f"{REPORT_PREFIX}.gop_y")
    return _respond(request, "Cảm ơn góp ý của bạn. Mình đã ghi nhận.", True)
