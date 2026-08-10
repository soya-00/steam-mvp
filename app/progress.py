"""Đọc tiến độ của một phiên nhập vai.

Cả không gian tư duy của học sinh lẫn trang tiến độ của giáo viên đều đọc từ
đây, để hai bên không bao giờ nói hai con số khác nhau về cùng một việc.
"""

from __future__ import annotations

import json
from datetime import datetime

from app.models import GuidedSession
from app.scenarios import Scenario


def transcript(gs: GuidedSession | None) -> list[dict]:
    if gs is None:
        return []
    try:
        rows = json.loads(gs.transcript or "[]")
    except json.JSONDecodeError:
        return []
    return rows if isinstance(rows, list) else []


def answered(gs: GuidedSession | None) -> list[dict]:
    return [row for row in transcript(gs) if row.get("answer")]


def stage_states(scenario: Scenario, gs: GuidedSession | None) -> list[dict]:
    """Bốn cấp độ kèm trạng thái: đã xong, đang làm, chưa tới."""
    stage_index = gs.stage_index if gs else 0
    finished = bool(gs and gs.finished)
    started = gs is not None

    out = []
    for i, stage in enumerate(scenario.stages):
        if finished or i < stage_index:
            state = "done"
        elif i == stage_index and started:
            state = "current"
        else:
            state = "todo"
        out.append({"name": stage.name, "state": state, "index": i})
    return out


def stages_done(scenario: Scenario, gs: GuidedSession | None) -> int:
    return sum(1 for s in stage_states(scenario, gs) if s["state"] == "done")


def word_count(gs: GuidedSession | None) -> int:
    return sum(len(row["answer"].split()) for row in answered(gs))


def last_activity(gs: GuidedSession | None) -> datetime | None:
    return gs.created_at if gs else None


def status(gs: GuidedSession | None) -> str:
    """`chua_bat_dau` · `dang_lam` · `da_xong` — dùng chung cho mọi chỗ đếm."""
    if gs is None:
        return "chua_bat_dau"
    if gs.finished:
        return "da_xong"
    if not answered(gs):
        return "chua_bat_dau"
    return "dang_lam"


STATUS_LABELS = {
    "chua_bat_dau": "Chưa bắt đầu",
    "dang_lam": "Đang làm",
    "da_xong": "Đã xong",
}


def summary(scenario: Scenario, gs: GuidedSession | None) -> dict:
    return {
        "stages": stage_states(scenario, gs),
        "stages_done": stages_done(scenario, gs),
        "stage_total": len(scenario.stages),
        "answers": len(answered(gs)),
        "words": word_count(gs),
        "finished": bool(gs and gs.finished),
        "status": status(gs),
        "last_activity": last_activity(gs),
    }
