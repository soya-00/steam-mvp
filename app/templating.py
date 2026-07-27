from __future__ import annotations

from fastapi import Request
from fastapi.templating import Jinja2Templates

from app.config import (
    FIELD_KEY_BY_NAME,
    PROJECT_CATEGORIES,
    STEAM_FIELDS,
    TEMPLATES_DIR,
    gemini_enabled,
)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

BADGE_LABELS = {
    "nhap_vai_dau_tien": "Lần nhập vai đầu tiên",
    "khoa_hoc": "Nhà khoa học tập sự",
    "cong_nghe": "Người dựng hệ thống",
    "ky_thuat": "Kỹ sư tập sự",
    "nghe_thuat": "Người kể chuyện thị giác",
    "toan": "Người đọc dữ liệu",
    "hoan_thanh_4_cap_do": "Đi hết bốn cấp độ",
    "chia_se_dau_tien": "Lần chia sẻ đầu tiên",
}

BADGE_ICONS = {
    "nhap_vai_dau_tien": "🎭",
    "khoa_hoc": "🔬",
    "cong_nghe": "💻",
    "ky_thuat": "⚙️",
    "nghe_thuat": "🎨",
    "toan": "📊",
    "hoan_thanh_4_cap_do": "🧭",
    "chia_se_dau_tien": "🔗",
}

CATEGORY_LABELS = {c["key"]: c["label"] for c in PROJECT_CATEGORIES}

PLATFORM_LABELS = {
    "coursera": "Coursera",
    "youtube": "YouTube",
    "khan": "Khan Academy",
}

FIELD_CLASSES = {
    "khoa_hoc": {
        "bar": "border-l-teal", "chip": "bg-teal-50 text-teal-700", "dot": "bg-teal",
        "art": "/static/img/fields/khoa_hoc.svg", "wash": "bg-teal-50",
        "ring": "ring-teal-100", "track": "bg-teal",
    },
    "cong_nghe": {
        "bar": "border-l-trunk", "chip": "bg-trunk-50 text-trunk", "dot": "bg-trunk",
        "art": "/static/img/fields/cong_nghe.svg", "wash": "bg-trunk-50",
        "ring": "ring-trunk-100", "track": "bg-trunk",
    },
    "ky_thuat": {
        "bar": "border-l-slate", "chip": "bg-slate-50 text-slate-700", "dot": "bg-slate",
        "art": "/static/img/fields/ky_thuat.svg", "wash": "bg-slate-50",
        "ring": "ring-slate-100", "track": "bg-slate",
    },
    "nghe_thuat": {
        "bar": "border-l-amber", "chip": "bg-amber-50 text-amber-900", "dot": "bg-amber",
        "art": "/static/img/fields/nghe_thuat.svg", "wash": "bg-amber-50",
        "ring": "ring-amber-100", "track": "bg-amber",
    },
    "toan": {
        "bar": "border-l-plum", "chip": "bg-plum-50 text-plum-700", "dot": "bg-plum",
        "art": "/static/img/fields/toan.svg", "wash": "bg-plum-50",
        "ring": "ring-plum-100", "track": "bg-plum",
    },
}

BEAT_CLASSES = {
    "context": "bg-trunk-50 border-trunk-100",
    "question": "bg-paper-raised border-hairline",
    "followup": "bg-paper-raised border-hairline",
    "closing": "bg-teal-50 border-teal-100",
    "ai": "bg-teal-50 border-teal-100",
}


def field_classes(field_name_or_key: str) -> dict:
    key = FIELD_KEY_BY_NAME.get(field_name_or_key, field_name_or_key)
    return FIELD_CLASSES.get(key, FIELD_CLASSES["khoa_hoc"])


def badge_label(badge_type: str) -> str:
    return BADGE_LABELS.get(badge_type, badge_type)


def badge_icon(badge_type: str) -> str:
    return BADGE_ICONS.get(badge_type, "🏅")


def is_htmx(request: Request) -> bool:
    return request.headers.get("HX-Request") == "true"


templates.env.globals.update(
    steam_fields=STEAM_FIELDS,
    field_key=FIELD_KEY_BY_NAME,
    project_categories=PROJECT_CATEGORIES,
    category_labels=CATEGORY_LABELS,
    platform_labels=PLATFORM_LABELS,
    badge_label=badge_label,
    badge_icon=badge_icon,
    field_classes=field_classes,
    beat_classes=BEAT_CLASSES,
    gemini_enabled=gemini_enabled,
)
