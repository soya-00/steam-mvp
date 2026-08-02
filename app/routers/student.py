from __future__ import annotations

import json
from urllib.parse import quote

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from itsdangerous import BadSignature, URLSafeSerializer
from sqlalchemy.orm import Session

from app.auth import get_current_user, session_key
from app.gemini import guided_reply, synthesis
from app.moderation import OK as SCREEN_OK
from app.moderation import REPLIES as SCREEN_REPLIES
from app.moderation import screen
from app.media import validate_url
from app.config import (
    FIELD_KEY_BY_NAME,
    FIELD_NAME_BY_KEY,
    PROJECT_CATEGORIES,
    SECRET_KEY,
    STEAM_FIELDS,
)
from app.db import get_db
from app.models import (
    Badge,
    ClassMembership,
    Feedback,
    GuidedSession,
    JournalEntry,
    Notification,
    PortfolioEntry,
    User,
)
from app.scenarios import (
    Scenario,
    all_scenarios,
    get_scenario,
    load_resources,
    scenarios_for_field,
)
from app.templating import templates

router = APIRouter()

_share = URLSafeSerializer(SECRET_KEY, salt="gals-share")

VALID_CATEGORIES = {c["key"] for c in PROJECT_CATEGORIES}


def _guard(user: User | None):
    if user is None:
        return RedirectResponse("/dang-nhap", status_code=303)
    if user.is_teacher:
        return RedirectResponse("/giao-vien", status_code=303)
    return None


def award_badge(db: Session, student_id: int, badge_type: str) -> Badge | None:
    existing = (
        db.query(Badge)
        .filter(Badge.student_id == student_id, Badge.badge_type == badge_type)
        .first()
    )
    if existing:
        return None
    badge = Badge(student_id=student_id, badge_type=badge_type)
    db.add(badge)
    return badge


def share_token(student_id: int) -> str:
    return _share.dumps({"sid": student_id})


def student_from_token(token: str) -> int | None:
    try:
        return _share.loads(token).get("sid")
    except BadSignature:
        return None


def _transcript(gs: GuidedSession) -> list[dict]:
    try:
        return json.loads(gs.transcript or "[]")
    except json.JSONDecodeError:
        return []


def _save_transcript(gs: GuidedSession, entries: list[dict]) -> None:
    gs.transcript = json.dumps(entries, ensure_ascii=False)


def _current_beat(scenario: Scenario, gs: GuidedSession):
    stage = scenario.stage_at(gs.stage_index)
    if stage is None:
        return None, None
    if gs.beat_index < len(stage.beats):
        return stage, stage.beats[gs.beat_index]
    if gs.beat_index == len(stage.beats) and stage.closing:
        return stage, None
    return stage, None


def _at_closing(scenario: Scenario, gs: GuidedSession) -> bool:
    stage = scenario.stage_at(gs.stage_index)
    return bool(stage and stage.closing and gs.beat_index == len(stage.beats))


def _advance(scenario: Scenario, gs: GuidedSession) -> None:
    stage = scenario.stage_at(gs.stage_index)
    if stage is None:
        gs.finished = True
        return

    last_index = len(stage.beats) if stage.closing else len(stage.beats) - 1
    if gs.beat_index < last_index:
        gs.beat_index += 1
        return

    if gs.stage_index + 1 < len(scenario.stages):
        gs.stage_index += 1
        gs.beat_index = 0
    else:
        gs.finished = True


def _sync_journal(db: Session, gs: GuidedSession, scenario: Scenario, user: User) -> JournalEntry:
    entry = (
        db.query(JournalEntry)
        .filter(
            JournalEntry.student_id == user.id,
            JournalEntry.scenario_id == scenario.id,
            JournalEntry.source == "guided",
        )
        .first()
    )
    answers = [t for t in _transcript(gs) if t.get("answer")]
    body = "\n\n".join(f"{t['label']}\n{t['answer']}" for t in answers)

    if entry is None:
        entry = JournalEntry(
            student_id=user.id,
            scenario_id=scenario.id,
            source="guided",
            title=f"Nhật ký — {scenario.title}",
        )
        db.add(entry)
    entry.content = body
    entry.ai_transcript = gs.transcript or "[]"
    return entry


def _answers_by_stage(scenario: Scenario, gs: GuidedSession) -> list[dict]:
    by_stage: dict[str, list[dict]] = {}
    for beat in _transcript(gs):
        if not beat.get("answer"):
            continue
        by_stage.setdefault(beat.get("stage", ""), []).append(beat)

    out = []
    for stage in scenario.stages:
        answers = by_stage.get(stage.name) or by_stage.get(stage.key) or []
        if answers:
            out.append({"name": stage.name, "answers": answers})
    return out


def _progress(scenario: Scenario, gs: GuidedSession) -> list[dict]:
    out = []
    for i, st in enumerate(scenario.stages):
        state = "done" if (gs.finished or i < gs.stage_index) else (
            "current" if i == gs.stage_index else "todo"
        )
        out.append({"name": st.name, "state": state, "index": i})
    return out


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
    portfolio = db.query(PortfolioEntry).filter(PortfolioEntry.student_id == user.id).all()
    badges = db.query(Badge).filter(Badge.student_id == user.id).all()
    memberships = db.query(ClassMembership).filter(ClassMembership.student_id == user.id).all()
    class_ids = [m.class_id for m in memberships]

    feedback = (
        db.query(Feedback)
        .filter(Feedback.student_id == user.id)
        .order_by(Feedback.created_at.desc())
        .all()
    )

    notif_q = db.query(Notification).filter(
        (Notification.class_id.is_(None) & Notification.student_id.is_(None))
        | (Notification.student_id == user.id)
    )
    if class_ids:
        notif_q = db.query(Notification).filter(
            (Notification.class_id.is_(None) & Notification.student_id.is_(None))
            | (Notification.student_id == user.id)
            | (Notification.class_id.in_(class_ids))
        )
    notifications = notif_q.order_by(Notification.created_at.desc()).limit(3).all()

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
            "scenarios": all_scenarios(),
        },
    )


@router.get("/du-an", response_class=HTMLResponse)
def choose_field(
    request: Request,
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user)) is not None:
        return redirect

    done_fields = {
        s.field
        for e in db.query(JournalEntry).filter(JournalEntry.student_id == user.id).all()
        if e.scenario_id and (s := get_scenario(e.scenario_id))
    }
    counts = {f["name"]: len(scenarios_for_field(f["name"])) for f in STEAM_FIELDS}

    return templates.TemplateResponse(
        request,
        "student/du_an_linh_vuc.html",
        {
            "user": user,
            "branch": "du_an",
            "counts": counts,
            "done_fields": done_fields,
        },
    )


@router.get("/du-an/linh-vuc/{field_key}", response_class=HTMLResponse)
def choose_scenario(
    request: Request,
    field_key: str,
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user)) is not None:
        return redirect

    field_name = FIELD_NAME_BY_KEY.get(field_key)
    if field_name is None:
        return RedirectResponse("/du-an", status_code=303)

    started = {
        gs.scenario_id: gs
        for gs in db.query(GuidedSession).filter(GuidedSession.student_id == user.id).all()
    }

    return templates.TemplateResponse(
        request,
        "student/du_an_kich_huong.html",
        {
            "user": user,
            "branch": "du_an",
            "field_name": field_name,
            "field_key": field_key,
            "scenarios": scenarios_for_field(field_name),
            "started": started,
        },
    )


@router.get("/du-an/{scenario_id}", response_class=HTMLResponse)
def scenario_intro(
    request: Request,
    scenario_id: str,
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user)) is not None:
        return redirect

    scenario = get_scenario(scenario_id)
    if scenario is None:
        return RedirectResponse("/du-an", status_code=303)

    gs = (
        db.query(GuidedSession)
        .filter(
            GuidedSession.student_id == user.id,
            GuidedSession.scenario_id == scenario_id,
        )
        .first()
    )

    return templates.TemplateResponse(
        request,
        "student/du_an_nhap_vai.html",
        {
            "user": user,
            "branch": "du_an",
            "scenario": scenario,
            "gs": gs,
        },
    )


@router.get("/du-an/{scenario_id}/khong-gian-tu-duy", response_class=HTMLResponse)
def workspace(
    request: Request,
    scenario_id: str,
    nhac: str = "",
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user)) is not None:
        return redirect

    scenario = get_scenario(scenario_id)
    if scenario is None:
        return RedirectResponse("/du-an", status_code=303)

    gs = (
        db.query(GuidedSession)
        .filter(
            GuidedSession.student_id == user.id,
            GuidedSession.scenario_id == scenario_id,
        )
        .first()
    )
    if gs is None:
        gs = GuidedSession(student_id=user.id, scenario_id=scenario_id)
        db.add(gs)
        award_badge(db, user.id, "nhap_vai_dau_tien")
        db.commit()

    stage, beat = _current_beat(scenario, gs)

    return templates.TemplateResponse(
        request,
        "student/workspace.html",
        {
            "user": user,
            "branch": "du_an",
            "scenario": scenario,
            "gs": gs,
            "stage": stage,
            "beat": beat,
            "at_closing": _at_closing(scenario, gs),
            "transcript": _transcript(gs),
            "progress": _progress(scenario, gs),
            "loi_nhac": SCREEN_REPLIES.get(nhac),
        },
    )


@router.post("/du-an/{scenario_id}/tiep", response_class=HTMLResponse)
def workspace_step(
    request: Request,
    scenario_id: str,
    tra_loi: str = Form(""),
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user)) is not None:
        return redirect

    scenario = get_scenario(scenario_id)
    if scenario is None:
        return RedirectResponse("/du-an", status_code=303)

    gs = (
        db.query(GuidedSession)
        .filter(
            GuidedSession.student_id == user.id,
            GuidedSession.scenario_id == scenario_id,
        )
        .first()
    )
    if gs is None or gs.finished:
        return RedirectResponse(f"/du-an/{scenario_id}/khong-gian-tu-duy", status_code=303)

    stage, beat = _current_beat(scenario, gs)
    entries = _transcript(gs)
    answer = tra_loi.strip()
    question = None

    needs_answer = _at_closing(scenario, gs) or (beat is not None and beat.needs_answer)
    if needs_answer and answer:
        verdict, _ = screen(answer)
        if verdict != SCREEN_OK:
            return RedirectResponse(
                f"/du-an/{scenario_id}/khong-gian-tu-duy?nhac={verdict}",
                status_code=303,
            )

    if _at_closing(scenario, gs):
        question = stage.closing
        entries.append(
            {
                "kind": "closing",
                "stage": stage.name,
                "label": f"Câu kết cấp độ · {stage.name}",
                "text": stage.closing,
                "answer": answer,
            }
        )
    elif beat is not None:
        if beat.needs_answer:
            question = beat.text
        entries.append(
            {
                "kind": beat.type,
                "stage": stage.name,
                "label": beat.label or stage.name,
                "text": beat.text,
                "answer": answer if beat.needs_answer else "",
            }
        )

    if question and answer:
        turn = sum(1 for t in entries if t.get("kind") == "ai")
        entries.append(
            {
                "kind": "ai",
                "stage": stage.name,
                "label": "Người đồng hành",
                "text": guided_reply(
                    scenario, stage, question, answer, turn, session_key(request)
                ),
                "answer": "",
            }
        )

    _save_transcript(gs, entries)
    _advance(scenario, gs)
    _sync_journal(db, gs, scenario, user)

    if gs.finished:
        award_badge(db, user.id, "hoan_thanh_4_cap_do")
        award_badge(db, user.id, FIELD_KEY_BY_NAME.get(scenario.field, "khoa_hoc"))
        if not gs.synthesis:
            gs.synthesis = synthesis(scenario, entries, session_key(request))

    db.commit()
    return RedirectResponse(f"/du-an/{scenario_id}/khong-gian-tu-duy", status_code=303)


@router.post("/du-an/{scenario_id}/lam-lai")
def workspace_restart(
    scenario_id: str,
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user)) is not None:
        return redirect
    gs = (
        db.query(GuidedSession)
        .filter(
            GuidedSession.student_id == user.id,
            GuidedSession.scenario_id == scenario_id,
        )
        .first()
    )
    if gs is not None:
        gs.stage_index = 0
        gs.beat_index = 0
        gs.finished = False
        gs.synthesis = ""
        gs.transcript = "[]"
        db.commit()
    return RedirectResponse(f"/du-an/{scenario_id}/khong-gian-tu-duy", status_code=303)


@router.get("/du-an/{scenario_id}/nop", response_class=HTMLResponse)
def submit_form(
    request: Request,
    scenario_id: str,
    loi: str = "",
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user)) is not None:
        return redirect

    scenario = get_scenario(scenario_id)
    if scenario is None:
        return RedirectResponse("/du-an", status_code=303)

    entry = (
        db.query(JournalEntry)
        .filter(
            JournalEntry.student_id == user.id,
            JournalEntry.scenario_id == scenario_id,
            JournalEntry.source == "guided",
        )
        .first()
    )

    return templates.TemplateResponse(
        request,
        "student/du_an_nop.html",
        {
            "user": user,
            "branch": "du_an",
            "scenario": scenario,
            "entry": entry,
            "loi": loi,
        },
    )


@router.post("/du-an/{scenario_id}/nop")
def submit_project(
    scenario_id: str,
    mo_ta: str = Form(""),
    anh: str = Form(""),
    video: str = Form(""),
    phan_loai: str = Form("ca_hai"),
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user)) is not None:
        return redirect

    scenario = get_scenario(scenario_id)
    if scenario is None:
        return RedirectResponse("/du-an", status_code=303)

    entry = (
        db.query(JournalEntry)
        .filter(
            JournalEntry.student_id == user.id,
            JournalEntry.scenario_id == scenario_id,
            JournalEntry.source == "guided",
        )
        .first()
    )
    if entry is None:
        entry = JournalEntry(
            student_id=user.id,
            scenario_id=scenario_id,
            source="guided",
            title=f"Nhật ký — {scenario.title}",
        )
        db.add(entry)
        db.flush()

    image_url, image_error = validate_url(anh)
    video_url, video_error = validate_url(video)
    if image_error or video_error:
        return RedirectResponse(
            f"/du-an/{scenario_id}/nop?loi={quote(image_error or video_error)}",
            status_code=303,
        )

    entry.image_url = image_url
    entry.video_url = video_url
    entry.submitted = True

    category = phan_loai if phan_loai in VALID_CATEGORIES else "ca_hai"
    portfolio = (
        db.query(PortfolioEntry)
        .filter(
            PortfolioEntry.student_id == user.id,
            PortfolioEntry.journal_entry_id == entry.id,
        )
        .first()
    )
    if portfolio is None:
        count = db.query(PortfolioEntry).filter(PortfolioEntry.student_id == user.id).count()
        portfolio = PortfolioEntry(
            student_id=user.id,
            journal_entry_id=entry.id,
            order_index=count,
        )
        db.add(portfolio)
    portfolio.category = category
    portfolio.description = mo_ta.strip() or scenario.description

    award_badge(db, user.id, FIELD_KEY_BY_NAME.get(scenario.field, "khoa_hoc"))
    db.commit()

    return RedirectResponse("/ho-so?vua-nop=1", status_code=303)


@router.get("/ho-so", response_class=HTMLResponse)
def portfolio_view(
    request: Request,
    vua_nop: str = "",
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user)) is not None:
        return redirect

    items = (
        db.query(PortfolioEntry)
        .filter(PortfolioEntry.student_id == user.id)
        .order_by(PortfolioEntry.order_index, PortfolioEntry.created_at)
        .all()
    )
    entries = (
        db.query(JournalEntry)
        .filter(JournalEntry.student_id == user.id)
        .order_by(JournalEntry.created_at.desc())
        .all()
    )

    feedback = (
        db.query(Feedback)
        .filter(Feedback.student_id == user.id)
        .order_by(Feedback.created_at.desc())
        .all()
    )
    feedback_for: dict[int, list[Feedback]] = {}
    for note in feedback:
        feedback_for.setdefault(note.journal_entry_id or 0, []).append(note)

    sessions = (
        db.query(GuidedSession)
        .filter(GuidedSession.student_id == user.id)
        .order_by(GuidedSession.created_at.desc())
        .all()
    )
    journeys = []
    for gs in sessions:
        scenario = get_scenario(gs.scenario_id)
        if scenario is None:
            continue
        journeys.append(
            {
                "scenario": scenario,
                "finished": gs.finished,
                "synthesis": gs.synthesis,
                "stages": _answers_by_stage(scenario, gs),
                "answer_count": len([t for t in _transcript(gs) if t.get("answer")]),
            }
        )

    return templates.TemplateResponse(
        request,
        "student/ho_so.html",
        {
            "user": user,
            "branch": "ho_so",
            "items": items,
            "entries": entries,
            "scenario_of": {e.id: get_scenario(e.scenario_id) for e in entries},
            "journeys": journeys,
            "feedback_for": feedback_for,
            "feedback_count": len(feedback),
            "answer_total": sum(j["answer_count"] for j in journeys),
            "just_submitted": bool(vua_nop),
            "token": share_token(user.id),
        },
    )


@router.post("/ho-so/{entry_id}/mo-ta", response_class=HTMLResponse)
def edit_description(
    request: Request,
    entry_id: int,
    mo_ta: str = Form(""),
    phan_loai: str = Form(""),
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user)) is not None:
        return redirect

    item = (
        db.query(PortfolioEntry)
        .filter(PortfolioEntry.id == entry_id, PortfolioEntry.student_id == user.id)
        .first()
    )
    if item is None:
        return RedirectResponse("/ho-so", status_code=303)

    item.description = mo_ta.strip()
    if phan_loai in VALID_CATEGORIES:
        item.category = phan_loai
    db.commit()

    return templates.TemplateResponse(
        request,
        "student/partials/portfolio_item.html",
        {"user": user, "item": item, "saved": True},
    )


@router.post("/ho-so/{entry_id}/chia-se", response_class=HTMLResponse)
def toggle_share(
    request: Request,
    entry_id: int,
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user)) is not None:
        return redirect

    item = (
        db.query(PortfolioEntry)
        .filter(PortfolioEntry.id == entry_id, PortfolioEntry.student_id == user.id)
        .first()
    )
    if item is None:
        return RedirectResponse("/ho-so", status_code=303)

    item.shared = not item.shared
    if item.shared:
        award_badge(db, user.id, "chia_se_dau_tien")
    db.commit()

    return templates.TemplateResponse(
        request,
        "student/partials/portfolio_item.html",
        {"user": user, "item": item, "saved": False},
    )


@router.get("/ho-so/chia-se", response_class=HTMLResponse)
def share_page(
    request: Request,
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user)) is not None:
        return redirect

    shared = (
        db.query(PortfolioEntry)
        .filter(PortfolioEntry.student_id == user.id, PortfolioEntry.shared.is_(True))
        .order_by(PortfolioEntry.order_index)
        .all()
    )
    return templates.TemplateResponse(
        request,
        "student/ho_so_chia_se.html",
        {
            "user": user,
            "branch": "ho_so",
            "shared": shared,
            "token": share_token(user.id),
        },
    )


@router.get("/p/{token}", response_class=HTMLResponse)
def public_portfolio(
    request: Request,
    token: str,
    db: Session = Depends(get_db),
):
    student_id = student_from_token(token)
    owner = db.get(User, student_id) if student_id else None
    if owner is None:
        return templates.TemplateResponse(request, "404.html", {"user": None}, status_code=404)

    items = (
        db.query(PortfolioEntry)
        .filter(PortfolioEntry.student_id == owner.id, PortfolioEntry.shared.is_(True))
        .order_by(PortfolioEntry.order_index)
        .all()
    )
    return templates.TemplateResponse(
        request,
        "student/public_portfolio.html",
        {"user": None, "owner": owner, "items": items},
    )


@router.get("/huy-hieu", response_class=HTMLResponse)
def badges_view(
    request: Request,
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user)) is not None:
        return redirect

    earned = {
        b.badge_type: b for b in db.query(Badge).filter(Badge.student_id == user.id).all()
    }

    catalogue = ["nhap_vai_dau_tien", "hoan_thanh_4_cap_do", "chia_se_dau_tien"]
    catalogue += [f["key"] for f in STEAM_FIELDS]

    unexplored = [f for f in STEAM_FIELDS if f["key"] not in earned]
    suggestion = None
    if unexplored:
        field = unexplored[0]
        pool = scenarios_for_field(field["name"])
        suggestion = {"field": field, "scenario": pool[0] if pool else None}

    return templates.TemplateResponse(
        request,
        "student/huy_hieu.html",
        {
            "user": user,
            "branch": "huy_hieu",
            "earned": earned,
            "catalogue": catalogue,
            "suggestion": suggestion,
        },
    )


@router.get("/tai-nguyen", response_class=HTMLResponse)
def resources_view(
    request: Request,
    linh_vuc: str = "",
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (redirect := _guard(user)) is not None:
        return redirect

    resources = load_resources()
    selected = FIELD_NAME_BY_KEY.get(linh_vuc)
    shown = {selected: resources.get(selected, [])} if selected else resources

    memberships = db.query(ClassMembership).filter(ClassMembership.student_id == user.id).all()
    class_ids = [m.class_id for m in memberships]

    notif_q = db.query(Notification).filter(
        (Notification.class_id.is_(None) & Notification.student_id.is_(None))
        | (Notification.student_id == user.id)
    )
    if class_ids:
        notif_q = db.query(Notification).filter(
            (Notification.class_id.is_(None) & Notification.student_id.is_(None))
            | (Notification.student_id == user.id)
            | (Notification.class_id.in_(class_ids))
        )
    notifications = notif_q.order_by(Notification.created_at.desc()).all()

    return templates.TemplateResponse(
        request,
        "student/tai_nguyen.html",
        {
            "user": user,
            "branch": "tai_nguyen",
            "shown": shown,
            "selected": selected,
            "selected_key": linh_vuc,
            "notifications": notifications,
        },
    )
