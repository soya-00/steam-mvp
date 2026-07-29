from __future__ import annotations

import pathlib
import re

from app.templating import BEAT_CLASSES, FIELD_CLASSES

CSS = pathlib.Path("static/css/app.css").read_text(encoding="utf-8")

# Class component tự định nghĩa — mất một cái là giao diện hỏng âm thầm.
COMPONENTS = [
    "card", "btn", "btn-primary", "btn-ghost", "chip", "branch-bar",
    "lift", "art-banner", "step-track", "step-fill", "rise", "pop",
    "prose-beat", "htmx-indicator", "spinner-dot",
    "answer-lines", "print-box", "print-page-break", "print-sheet", "no-print",
]


def _present(token: str) -> bool:
    escaped = token.replace(":", "\\:").replace(".", "\\.").replace("/", "\\/")
    return f".{escaped}" in CSS or f".{token}" in CSS


def test_component_classes_survive_build():
    missing = [c for c in COMPONENTS if not _present(c)]
    assert missing == [], f"class biến mất khỏi CSS build: {missing}"


def test_field_and_beat_classes_survive_build():
    tokens: set[str] = set()
    for spec in FIELD_CLASSES.values():
        for key, value in spec.items():
            if key == "art":
                continue
            tokens.update(value.split())
    for value in BEAT_CLASSES.values():
        tokens.update(value.split())

    missing = [t for t in sorted(tokens) if not _present(t)]
    assert missing == [], f"class trong dữ liệu không có trong CSS: {missing}"


def test_field_artwork_files_exist():
    for spec in FIELD_CLASSES.values():
        path = pathlib.Path(spec["art"].lstrip("/"))
        assert path.exists(), spec["art"]
        head = path.read_text(encoding="utf-8")[:200]
        assert 'aria-hidden="true"' in head


def test_no_dynamic_class_concatenation_in_templates():
    # Cái bẫy đã cắn hai lần: Tailwind quét tĩnh, ghép chuỗi là class biến mất.
    pattern = re.compile(r'(?:border-l|bg|text|ring)-\{\{')
    offenders = []
    for p in pathlib.Path("app/templates").rglob("*.html"):
        if pattern.search(p.read_text(encoding="utf-8")):
            offenders.append(str(p))
    assert offenders == []
