from __future__ import annotations

import pathlib
import re

from app.templating import BEAT_CLASSES, FIELD_CLASSES

CSS = pathlib.Path("static/css/app.css").read_text(encoding="utf-8")

# Class component tự định nghĩa — mất một cái là giao diện hỏng âm thầm.
COMPONENTS = [
    "card", "btn", "btn-primary", "btn-ghost", "chip",
    "lift", "art-banner", "step-track", "step-fill", "rise", "pop",
    "prose-beat", "htmx-indicator", "spinner-dot",
    "answer-lines", "print-box", "print-page-break", "print-sheet", "no-print",
    "microlabel", "app-tabs", "tab", "panel", "composer", "ruled", "tile", "filter-chip",
    "role-card", "fact-item", "dashed-slot", "ring-track", "disclose",
    "wordmark", "mung-burst", "disclose-corner",
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


# Bảng màu bản tối và bản tương phản cao. Mất một token là cả một mặt phẳng
# rơi về giá trị bản sáng mà không có lỗi nào báo.
THEMED_TOKENS = [
    "--c-paper", "--c-paper-raised", "--c-sunken", "--c-raised-2",
    "--c-ink", "--c-ink-soft", "--c-ink-faint", "--c-hairline",
    "--c-field-line", "--c-on-accent", "--c-focus", "--c-knob",
    "--c-trunk", "--c-trunk-50", "--c-trunk-700",
    "--c-teal", "--c-amber", "--c-plum", "--c-slate",
    "--c-sci", "--c-tech", "--c-eng", "--c-art", "--c-math",
]


def _block(selector: str) -> str:
    # Bản rút gọn bỏ dấu nháy trong bộ chọn thuộc tính.
    for form in (selector, selector.replace('"', "")):
        at = CSS.find(form + "{")
        if at != -1:
            return CSS[at : CSS.index("}", at)]
    raise AssertionError(f"không tìm thấy khối {selector} trong CSS build")


def test_dark_theme_redefines_every_themed_token():
    dark = _block(':root[data-theme="dark"]')
    missing = [t for t in THEMED_TOKENS if t + ":" not in dark]
    assert missing == [], f"bản tối thiếu token: {missing}"


def test_dark_theme_declares_color_scheme():
    # Thiếu dòng này thì thanh cuộn và ô chọn ngày của trình duyệt vẫn trắng.
    assert "color-scheme:dark" in _block(':root[data-theme="dark"]')


def test_high_contrast_layers_over_both_themes():
    for selector in (':root[data-contrast="cao"]',
                     ':root[data-theme="dark"][data-contrast="cao"]'):
        block = _block(selector)
        for token in ("--c-paper", "--c-ink", "--c-hairline", "--c-field-line"):
            assert token + ":" in block, f"{selector} thiếu {token}"


def test_system_contrast_still_works_without_javascript():
    assert "prefers-contrast" in CSS


def test_components_never_hardcode_a_theme_colour():
    # Mọi màu phải đi qua token, nếu không bản tối sẽ có những mảng trắng sót lại.
    blocks = re.findall(
        r"\.(?:btn-primary|tile|menu-panel|filter-chip|band)[^{]*\{([^}]*)\}", CSS
    )
    assert blocks, "không bắt được component nào để soi"
    offenders = [d for d in blocks if re.search(r"#(?:fff|ffffff|000|000000)\b", d)]
    assert offenders == [], f"màu cắm cứng trong component: {offenders}"


def test_printing_forces_the_light_palette():
    at = CSS.index("@media print")
    head = CSS[at : at + 900].replace(" ", "")
    # Bản rút gọn viết #ffffff thành #fff.
    assert "--c-paper:#fff" in head
