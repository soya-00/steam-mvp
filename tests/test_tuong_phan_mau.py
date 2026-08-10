"""Đo tương phản của bảng màu thay vì tin vào mắt.

Bảng màu thật nằm trong `src/input.css`; phép thử đọc thẳng từ đó, nên sửa một
mã màu mà làm tụt tương phản là đỏ ngay, không đợi ai nhìn ra.

Ngưỡng theo WCAG 2.2: 4.5 cho chữ thường, 3.0 cho chữ lớn và cho những đường
kẻ mang thông tin (viền ô nhập, rãnh công tắc).
"""

from __future__ import annotations

import pathlib
import re

CSS = pathlib.Path("src/input.css").read_text(encoding="utf-8")

CHU_THUONG = 4.5
CHU_LON = 3.0
DUONG_KE = 3.0


def _block(selector: str) -> dict[str, str]:
    at = CSS.index(selector + " {")
    body = CSS[at : CSS.index("\n}", at)]
    return dict(re.findall(r"(--c-[a-z0-9-]+):\s*(#[0-9a-fA-F]{6})", body))


SANG = _block(":root")
TOI = {**SANG, **_block(':root[data-theme="dark"]')}
SANG_CAO = {**SANG, **_block(':root[data-contrast="cao"]')}
TOI_CAO = {**TOI, **_block(':root[data-theme="dark"][data-contrast="cao"]')}

BANG = {
    "sáng": SANG,
    "tối": TOI,
    "sáng + tương phản cao": SANG_CAO,
    "tối + tương phản cao": TOI_CAO,
}


def _luminance(hex_colour: str) -> float:
    raw = hex_colour.lstrip("#")
    channels = [int(raw[i : i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def ratio(fg: str, bg: str) -> float:
    a, b = _luminance(fg), _luminance(bg)
    return (max(a, b) + 0.05) / (min(a, b) + 0.05)


def _check(failures: list[str], theme: str, tokens: dict[str, str],
           fg: str, bg: str, need: float) -> None:
    if fg not in tokens or bg not in tokens:
        return
    got = ratio(tokens[fg], tokens[bg])
    if got < need:
        failures.append(
            f"{theme}: {fg} ({tokens[fg]}) trên {bg} ({tokens[bg]}) "
            f"= {got:.2f}, cần {need}"
        )


SURFACES = ["--c-paper", "--c-paper-raised", "--c-sunken", "--c-raised-2"]
FAMILIES = ["trunk", "teal", "amber", "plum", "slate", "sci", "tech", "eng", "art", "math"]

# Hai màu này ở bản sáng quá sáng để đội chữ trắng — amber được 2.9:1, art được
# 3.8:1. Thay vì kéo cả hai tối lại và mất chất, chúng chỉ được dùng làm màu
# chữ và mảng nhạt; `test_the_two_bright_families_are_never_a_text_fill` canh
# đúng chuyện đó.
KHONG_LAM_NEN_CHU = {"amber", "art"}


def test_body_text_reads_on_every_surface():
    failures: list[str] = []
    for theme, tokens in BANG.items():
        for surface in SURFACES:
            _check(failures, theme, tokens, "--c-ink", surface, CHU_THUONG)
            _check(failures, theme, tokens, "--c-ink-soft", surface, CHU_THUONG)
            # Chữ mờ đỡ nhãn phụ và placeholder — vẫn là chữ, vẫn 4.5.
            _check(failures, theme, tokens, "--c-ink-faint", surface, CHU_THUONG)
    assert failures == [], "\n".join(failures)


def test_each_branch_colour_reads_on_its_own_wash():
    failures: list[str] = []
    for theme, tokens in BANG.items():
        for family in FAMILIES:
            _check(failures, theme, tokens,
                   f"--c-{family}-700", f"--c-{family}-50", CHU_THUONG)
    assert failures == [], "\n".join(failures)


def test_accent_fills_carry_their_own_label():
    failures: list[str] = []
    for theme, tokens in BANG.items():
        for family in FAMILIES:
            if family in KHONG_LAM_NEN_CHU:
                continue
            _check(failures, theme, tokens, "--c-on-accent", f"--c-{family}", CHU_THUONG)
    assert failures == [], "\n".join(failures)


def test_the_two_bright_families_are_never_a_text_fill():
    offenders = []
    for path in pathlib.Path("app/templates").rglob("*.html"):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for family in KHONG_LAM_NEN_CHU:
                # `bg-amber-50` và `bg-amber-700` vẫn được; chỉ cấm nền đặc.
                if re.search(rf"\bbg-{family}(?![-\w])", line):
                    offenders.append(f"{path}:{number}  {line.strip()[:70]}")
    assert offenders == [], "nền đặc quá sáng để đội chữ:\n" + "\n".join(offenders)


def test_load_bearing_lines_clear_three_to_one():
    # Viền ô nhập, rãnh công tắc, ô cấp độ rỗng: mất là mất luôn thông tin.
    failures: list[str] = []
    for theme, tokens in BANG.items():
        for surface in SURFACES:
            _check(failures, theme, tokens, "--c-field-line", surface, DUONG_KE)
    assert failures == [], "\n".join(failures)


def test_focus_ring_is_visible_on_every_surface():
    failures: list[str] = []
    for theme, tokens in BANG.items():
        for surface in SURFACES:
            _check(failures, theme, tokens, "--c-focus", surface, DUONG_KE)
    assert failures == [], "\n".join(failures)


def test_the_teacher_band_reads_in_both_themes():
    failures: list[str] = []
    for theme, tokens in BANG.items():
        _check(failures, theme, tokens, "--c-band-ink", "--c-band", CHU_LON)
        _check(failures, theme, tokens, "--c-band-ink-soft", "--c-band", CHU_THUONG)
        _check(failures, theme, tokens, "--c-band-btn-ink", "--c-band-btn", CHU_THUONG)
        _check(failures, theme, tokens, "--c-band-btn", "--c-band", DUONG_KE)
        _check(failures, theme, tokens, "--c-band-line", "--c-paper", DUONG_KE)
    assert failures == [], "\n".join(failures)


def test_dark_mode_never_paints_pure_white_text_or_pure_black_ground():
    # Trắng tinh trên đen tuyền là mức tương phản gắt nhất màn hình làm được và
    # nó rung; đen tuyền còn làm nhoè khi cuộn trên màn OLED. Chỉ bản tương
    # phản cao mới được phép, vì ở đó người dùng đã chủ động đổi lấy điều đó.
    assert TOI["--c-ink"].lower() != "#ffffff"
    assert TOI["--c-paper"].lower() != "#000000"


def test_dark_surfaces_get_lighter_as_they_stack():
    # Càng nổi lên càng sáng. Ngược lại thì menu và hộp thoại trông như cái lỗ.
    steps = [_luminance(TOI[s]) for s in SURFACES if s != "--c-paper"]
    assert steps == sorted(steps), "bề mặt bản tối không tăng dần độ sáng"
    assert _luminance(TOI["--c-paper"]) < steps[0]
