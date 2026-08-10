from __future__ import annotations

import json
from dataclasses import dataclass, field as dc_field
from functools import lru_cache

from app.config import DATA_DIR

BEAT_TYPES = {"context", "question", "followup"}

STAGE_ORDER = ("hieu_van_de", "dong_cam", "sang_tao", "phan_chieu")

STAGE_LABELS = {
    "hieu_van_de": "Hiểu vấn đề",
    "dong_cam": "Đồng cảm",
    "sang_tao": "Sáng tạo",
    "phan_chieu": "Phản chiếu",
}


STAGE_HINTS = {
    "hieu_van_de": (
        "Thử tách đôi: điều nào bạn đọc thẳng được từ dữ kiện, điều nào bạn đang tự suy ra?",
        "Con số nào ở đây đang thiếu mẫu số — biết một phần mà không biết trên tổng bao "
        "nhiêu thì nói lên được điều gì?",
        "Nếu chỉ được hỏi thêm đúng một câu trước khi kết luận, bạn sẽ hỏi gì?",
    ),
    "dong_cam": (
        "Liệt kê nhanh những người bị ảnh hưởng — kể cả người không xuất hiện trong tình huống.",
        "Mỗi người đang sợ mất điều gì? Người ta hay im lặng vì sợ chứ không phải vì không biết.",
        "Câu bạn định hỏi, nếu người nghe đang lo bị đổ lỗi thì họ sẽ hiểu thành gì?",
    ),
    "sang_tao": (
        "Viết ra hai phương án khác hẳn nhau rồi mới chọn — phương án đầu tiên hiếm khi là "
        "phương án tốt nhất.",
        "Nếu chỉ còn một tuần và không thêm đồng nào, bạn sẽ cắt phần nào trước?",
        "Ai là người phải thực hiện đề xuất của bạn? Việc đó có khả thi với họ không?",
    ),
    "phan_chieu": (
        "Nếu điều bạn đang tin là sai, dấu hiệu đầu tiên cho thấy nó sai sẽ là gì?",
        "Có cách giải thích nào khác cũng khớp với đúng những dữ kiện này không?",
        "Chỗ nào trong lập luận của bạn đang dựa vào một điều chưa ai kiểm chứng?",
    ),
}


def stage_hints(stage_key: str) -> tuple[str, ...]:
    return STAGE_HINTS.get(stage_key, ())


class ScenarioError(ValueError):
    pass


@dataclass(frozen=True)
class Beat:
    type: str
    label: str
    text: str
    facts: tuple[str, ...] = ()

    @property
    def needs_answer(self) -> bool:
        return self.type in ("question", "followup")


@dataclass(frozen=True)
class Stage:
    key: str
    name: str
    beats: tuple[Beat, ...]
    closing: str

    @property
    def question_count(self) -> int:
        return sum(1 for b in self.beats if b.needs_answer) + (1 if self.closing else 0)


@dataclass(frozen=True)
class Scenario:
    id: str
    field: str
    title: str
    description: str
    has_female_protagonist: bool
    role: str = ""
    career_group: str = ""
    knowledge: str = ""
    creation_output: str = ""
    disclaimer: str = ""
    protagonist: str = ""
    image_url: str = ""
    image_alt: str = ""
    domain_skills: tuple[str, ...] = ()
    stages: tuple[Stage, ...] = dc_field(default_factory=tuple)

    @property
    def stage_count(self) -> int:
        return len(self.stages)

    @property
    def total_questions(self) -> int:
        return sum(s.question_count for s in self.stages)

    def stage_at(self, index: int) -> Stage | None:
        if 0 <= index < len(self.stages):
            return self.stages[index]
        return None


def _require(raw: dict, key: str, ctx: str) -> object:
    if key not in raw:
        raise ScenarioError(f"{ctx}: thiếu trường bắt buộc '{key}'")
    return raw[key]


def _parse_beat(raw: dict, ctx: str) -> Beat:
    btype = str(_require(raw, "type", ctx))
    if btype not in BEAT_TYPES:
        raise ScenarioError(f"{ctx}: type '{btype}' không hợp lệ (cho phép: {sorted(BEAT_TYPES)})")
    text = str(_require(raw, "text", ctx)).strip()
    if not text:
        raise ScenarioError(f"{ctx}: 'text' rỗng")

    facts = tuple(str(f).strip() for f in raw.get("facts", []) if str(f).strip())
    if btype == "context" and not facts:
        raise ScenarioError(f"{ctx}: nhịp bối cảnh phải có 'facts' để tóm tắt ở cột dữ kiện")

    return Beat(
        type=btype,
        label=str(raw.get("label", "")).strip(),
        text=text,
        facts=facts,
    )


def _parse_stage(raw: dict, ctx: str) -> Stage:
    key = str(_require(raw, "key", ctx))
    if key not in STAGE_LABELS:
        raise ScenarioError(f"{ctx}: key cấp độ '{key}' không thuộc {list(STAGE_LABELS)}")
    beats_raw = _require(raw, "beats", ctx)
    if not isinstance(beats_raw, list) or not beats_raw:
        raise ScenarioError(f"{ctx}: 'beats' phải là danh sách không rỗng")
    beats = tuple(_parse_beat(b, f"{ctx} · beat #{i + 1}") for i, b in enumerate(beats_raw))
    return Stage(
        key=key,
        name=str(raw.get("name") or STAGE_LABELS[key]),
        beats=beats,
        closing=str(raw.get("closing", "")).strip(),
    )


def _parse_scenario(raw: dict, ctx: str) -> Scenario:
    sid = str(_require(raw, "id", ctx))
    ctx = f"{ctx} ('{sid}')"
    stages_raw = _require(raw, "stages", ctx)
    if not isinstance(stages_raw, list) or not stages_raw:
        raise ScenarioError(f"{ctx}: 'stages' phải là danh sách không rỗng")

    stages = tuple(
        _parse_stage(s, f"{ctx} · cấp độ #{i + 1}") for i, s in enumerate(stages_raw)
    )

    seen = [s.key for s in stages]
    if len(set(seen)) != len(seen):
        raise ScenarioError(f"{ctx}: có cấp độ bị lặp key")

    return Scenario(
        id=sid,
        field=str(_require(raw, "field", ctx)),
        title=str(_require(raw, "title", ctx)),
        description=str(raw.get("description", "")).strip(),
        has_female_protagonist=bool(raw.get("has_female_protagonist", False)),
        role=str(raw.get("role", "")).strip(),
        career_group=str(raw.get("career_group", "")).strip(),
        knowledge=str(raw.get("knowledge", "")).strip(),
        creation_output=str(raw.get("creation_output", "")).strip(),
        disclaimer=str(raw.get("disclaimer", "")).strip(),
        protagonist=str(raw.get("protagonist", "")).strip(),
        image_url=str(raw.get("image_url", "")).strip(),
        image_alt=str(raw.get("image_alt", "")).strip(),
        domain_skills=tuple(str(s) for s in raw.get("domain_skills", [])),
        stages=stages,
    )


@lru_cache(maxsize=1)
def load_scenarios() -> tuple[Scenario, ...]:
    path = DATA_DIR / "scenarios.json"
    if not path.exists():
        raise ScenarioError(f"Không tìm thấy {path}")

    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ScenarioError("scenarios.json phải là một mảng JSON")

    scenarios = tuple(
        _parse_scenario(item, f"scenarios.json · mục #{i + 1}") for i, item in enumerate(raw)
    )

    ids = [s.id for s in scenarios]
    if len(set(ids)) != len(ids):
        raise ScenarioError("scenarios.json: có id kịch huống bị trùng")

    return scenarios


def all_scenarios() -> tuple[Scenario, ...]:
    return load_scenarios()


def get_scenario(scenario_id: str) -> Scenario | None:
    return next((s for s in load_scenarios() if s.id == scenario_id), None)


def scenarios_for_field(field_name: str) -> list[Scenario]:
    return [s for s in load_scenarios() if s.field == field_name]


@lru_cache(maxsize=1)
def load_resources() -> dict:
    path = DATA_DIR / "resources.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))
