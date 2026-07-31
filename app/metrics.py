from __future__ import annotations

import logging
import threading
from collections import Counter

log = logging.getLogger("gals.metrics")

_lock = threading.Lock()
_counts: Counter[str] = Counter()

SCREEN_PREFIX = "screen"
REPORT_PREFIX = "report"


def bump(name: str) -> None:
    with _lock:
        _counts[name] += 1
        total = _counts[name]
    log.info("đếm %s = %d", name, total)


def snapshot() -> dict[str, int]:
    with _lock:
        return dict(_counts)


def reset() -> None:
    with _lock:
        _counts.clear()
