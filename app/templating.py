from __future__ import annotations

from fastapi import Request
from fastapi.templating import Jinja2Templates
from itsdangerous import BadSignature, URLSafeSerializer

from app.config import (
    FIELD_KEY_BY_NAME,
    PROJECT_CATEGORIES,
    STEAM_FIELDS,
    TEMPLATES_DIR,
    SECRET_KEY,
    SESSION_COOKIE,
    gemini_enabled,
)
from app.csrf import csrf_context
from app.scenarios import get_scenario

_session = URLSafeSerializer(SECRET_KEY, salt="gals-session")


def menu_context(request: Request) -> dict:
    """Danh sách lớp cho bảng tài khoản. Chỉ truy vấn khi người đang đăng nhập
    là giáo viên — học sinh và khách không tốn thêm câu truy vấn nào."""
    raw = request.cookies.get(SESSION_COOKIE)
    if not raw:
        return {}
    try:
        uid = _session.loads(raw).get("uid")
    except BadSignature:
        return {}
    if uid is None:
        return {}

    from app.db import SessionLocal
    from app.models import Class, User

    with SessionLocal() as db:
        viewer = db.get(User, uid)
        if viewer is None or not viewer.can_teach:
            return {}
        classes = (
            db.query(Class).filter(Class.teacher_id == viewer.id).order_by(Class.name).all()
        )
        return {"menu_classes": [{"id": c.id, "name": c.name} for c in classes]}


templates = Jinja2Templates(
    directory=str(TEMPLATES_DIR),
    context_processors=[menu_context, csrf_context],
)

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
        "chip": "bg-sci-50 text-sci-700", "dot": "bg-sci",
        "art": "/static/img/fields/khoa_hoc.svg", "wash": "bg-sci-50",
        "ring": "ring-sci-100", "track": "bg-sci", "top": "border-t-sci",
        "soft": "bg-sci-50 border-sci-100", "ink": "text-sci-700",
    },
    "cong_nghe": {
        "chip": "bg-tech-50 text-tech-700", "dot": "bg-tech",
        "art": "/static/img/fields/cong_nghe.svg", "wash": "bg-tech-50",
        "ring": "ring-tech-100", "track": "bg-tech", "top": "border-t-tech",
        "soft": "bg-tech-50 border-tech-100", "ink": "text-tech-700",
    },
    "ky_thuat": {
        "chip": "bg-eng-50 text-eng-700", "dot": "bg-eng",
        "art": "/static/img/fields/ky_thuat.svg", "wash": "bg-eng-50",
        "ring": "ring-eng-100", "track": "bg-eng", "top": "border-t-eng",
        "soft": "bg-eng-50 border-eng-100", "ink": "text-eng-700",
    },
    "nghe_thuat": {
        "chip": "bg-art-50 text-art-700", "dot": "bg-art",
        "art": "/static/img/fields/nghe_thuat.svg", "wash": "bg-art-50",
        "ring": "ring-art-100", "track": "bg-art", "top": "border-t-art",
        "soft": "bg-art-50 border-art-100", "ink": "text-art-700",
    },
    "toan": {
        "chip": "bg-math-50 text-math-700", "dot": "bg-math",
        "art": "/static/img/fields/toan.svg", "wash": "bg-math-50",
        "ring": "ring-math-100", "track": "bg-math", "top": "border-t-math",
        "soft": "bg-math-50 border-math-100", "ink": "text-math-700",
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
    scenario_of_id=get_scenario,
)
