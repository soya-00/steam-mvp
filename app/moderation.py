from __future__ import annotations

import re
import unicodedata

MAX_INPUT_CHARS = 2000

OK = "ok"
PROFANITY = "profanity"
NONSENSE = "nonsense"
INJECTION = "injection"
CRISIS = "crisis"
TOO_LONG = "too_long"

_VI_PROFANITY_WORDS = {
    "địt", "đụ", "cặc", "lồn", "buồi", "đéo", "đĩ", "cứt",
}

_VI_PROFANITY_PHRASES = (
    "đm", "đmm", "đcm", "đkm", "địt mẹ", "đụ má", "chó chết", "khốn nạn",
    "mẹ mày", "bố mày", "con đĩ", "thằng ngu", "óc chó", "súc vật", "mất dạy",
)

_ASCII_PROFANITY_WORDS = {
    "dm", "dmm", "vcl", "vl", "cmm", "clm", "clgt", "dcm", "dkm", "vkl", "vloz",
    "fuck", "fucking", "fuk", "shit", "bitch", "asshole", "bastard", "dick",
    "cunt", "wtf", "stfu", "retard",
}

_INJECTION = (
    "bỏ qua hướng dẫn", "bỏ qua mọi hướng dẫn", "quên hết hướng dẫn",
    "quên mọi thứ", "không cần tuân theo", "bỏ qua quy tắc",
    "ignore previous", "ignore all previous", "ignore your instructions",
    "disregard previous", "forget your instructions", "forget everything",
    "system prompt", "your prompt", "prompt hệ thống", "lời nhắc hệ thống",
    "you are now", "pretend you are", "jailbreak", "developer mode",
    "bây giờ bạn là", "không còn là trợ lý",
)

_VI_CRISIS = (
    "tự tử", "tự sát", "muốn chết", "không muốn sống", "kết thúc cuộc đời",
    "làm hại bản thân", "tự làm đau", "rạch tay", "tự cắt tay",
    "biến mất khỏi thế giới", "sống làm gì nữa", "chết cho xong",
)

_ASCII_CRISIS = (
    "kill myself", "suicide", "want to die", "end my life", "self harm",
    "selfharm", "hurt myself",
)

REPLIES = {
    PROFANITY: (
        "Mình bỏ qua đoạn vừa rồi nhé. Quay lại chuyện đang bàn thôi — "
        "bạn kể tiếp điều bạn để ý thấy đi."
    ),
    NONSENSE: (
        "Mình chưa đọc được đoạn này. Bạn thử viết lại bằng một câu bình thường xem sao?"
    ),
    INJECTION: (
        "Mình vẫn làm đúng việc của mình thôi: hỏi lại để bạn tự nghĩ ra. "
        "Ta quay lại tình huống nhé."
    ),
    CRISIS: (
        "Cảm ơn bạn đã nói ra. Mình chỉ là một công cụ học tập nên không giúp được "
        "chuyện này, và mình không muốn trả lời qua loa một điều quan trọng như vậy.\n\n"
        "Bạn nói với một người lớn mà bạn tin được nhé — bố mẹ, người thân, thầy cô, "
        "hoặc cán bộ tư vấn tâm lý ở trường. Ở Việt Nam còn có Tổng đài quốc gia bảo vệ "
        "trẻ em số 111, miễn phí và gọi được suốt ngày đêm.\n\n"
        "Khi nào bạn thấy ổn hơn thì quay lại đây, mình vẫn ở đây."
    ),
    TOO_LONG: (
        "Đoạn này dài quá nên mình chưa đọc hết được. Bạn tóm lại trong vài câu giúp mình nhé."
    ),
}


def _strip_accents(text: str) -> str:
    nfd = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in nfd if unicodedata.category(ch) != "Mn")


def _normalise(text: str) -> str:
    lowered = text.lower()
    collapsed = re.sub(r"[^\w\sÀ-ỹ]+", " ", lowered)
    return re.sub(r"\s+", " ", collapsed).strip()


def _contains_phrase(haystack: str, needles) -> bool:
    return any(needle in haystack for needle in needles)


def _has_profanity(text: str) -> bool:
    norm = _normalise(text)
    tokens = set(norm.split())

    if tokens & _VI_PROFANITY_WORDS:
        return True
    if tokens & _ASCII_PROFANITY_WORDS:
        return True
    return _contains_phrase(norm, _VI_PROFANITY_PHRASES)


_KEYBOARD_ROWS = ("qwertyuiop", "asdfghjkl", "zxcvbnm", "1234567890")
_KEYBOARD_RUN = 5


def _is_keyboard_run(word: str) -> bool:
    if len(word) < _KEYBOARD_RUN:
        return False
    for row in _KEYBOARD_ROWS:
        back = row[::-1]
        for start in range(len(word) - _KEYBOARD_RUN + 1):
            chunk = word[start : start + _KEYBOARD_RUN]
            if chunk in row or chunk in back:
                return True
    return False


def _is_nonsense(text: str) -> bool:
    stripped = _normalise(text)
    if not stripped:
        return True

    letters = [c for c in stripped if c.isalpha()]
    if len(letters) < 2:
        return True

    if re.search(r"(.)\1{5,}", stripped):
        return True

    words = stripped.split()
    long_words = [w for w in words if len(w) >= 4]
    if long_words:
        vowelless = [w for w in long_words if not re.search(r"[aeiouyàáảãạăâeêiìíîoôơuưy]", w)]
        if len(vowelless) == len(long_words):
            return True

    for word in words:
        bare = _strip_accents(word)
        if len(bare) >= 5 and re.search(r"[^aeiouy\W\d]{4,}", bare):
            return True
        if len(bare) >= 8:
            vowels = len(re.findall(r"[aeiouy]", bare))
            if vowels / len(bare) < 0.25:
                return True
        if _is_keyboard_run(bare):
            return True

    return False


def screen(text: str) -> tuple[str, str | None]:
    raw = (text or "").strip()

    if len(raw) > MAX_INPUT_CHARS:
        return TOO_LONG, REPLIES[TOO_LONG]

    norm = _normalise(raw)

    if _contains_phrase(norm, _VI_CRISIS) or _contains_phrase(norm, _ASCII_CRISIS):
        return CRISIS, REPLIES[CRISIS]

    if _contains_phrase(norm, _INJECTION):
        return INJECTION, REPLIES[INJECTION]

    if _has_profanity(raw):
        return PROFANITY, REPLIES[PROFANITY]

    if _is_nonsense(raw):
        return NONSENSE, REPLIES[NONSENSE]

    return OK, None
