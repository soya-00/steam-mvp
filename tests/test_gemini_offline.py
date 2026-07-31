from __future__ import annotations

from app import gemini
from app.gemini import (
    _USAGE_MAX_KEYS,
    IDEA_TAG,
    _spend,
    _usage,
    freeform_reply,
    quota_left,
    split_idea,
)
from app.moderation import REPLIES
from app.scenarios import all_scenarios


def test_split_idea_roundtrip():
    text = "Nghe hay đấy! Kể thêm đi?\n" + IDEA_TAG + " Hộp báo triệu chứng ẩn danh"
    reply, idea = split_idea(text)
    assert IDEA_TAG not in reply
    assert idea == "Hộp báo triệu chứng ẩn danh"
    assert split_idea("Không có gì đặc biệt.") == ("Không có gì đặc biệt.", None)


def test_offline_freeform_replies_and_offers_ideas():
    msg = "Em thấy nhiều bạn lớp em bỏ bữa sáng vì nhà xa, phải đi học từ sáu giờ."
    turn0, idea0 = freeform_reply([], msg, "t-off-0")
    assert turn0
    history = [{"role": "user", "text": msg}, {"role": "ai", "text": turn0}]
    turn1, idea1 = freeform_reply(history, msg, "t-off-1")
    assert turn1
    assert idea1, "chế độ ngoại tuyến phải thỉnh thoảng gợi lưu ý tưởng"


def test_blocked_input_returns_fixed_reply_without_engaging():
    reply, idea = freeform_reply([], "vcl chán vl", "t-block")
    assert reply == REPLIES["profanity"]
    assert idea is None


def test_offline_guided_reply_exists_for_every_stage():
    s = all_scenarios()[0]
    for stage in s.stages:
        reply = gemini.guided_reply(s, stage, "Câu hỏi?", "Em nghĩ là do tải.", 0, "t-guided")
        assert reply and len(reply) > 20


def test_usage_dict_is_bounded():
    _usage.clear()
    for i in range(_USAGE_MAX_KEYS * 2):
        _spend(f"khach-{i}")
    assert len(_usage) <= _USAGE_MAX_KEYS

    _usage.clear()
    key = "hoc-sinh-A"
    for _ in range(5):
        _spend(key)
    for i in range(_USAGE_MAX_KEYS):
        _spend(f"khach-moi-{i}")
    assert len(_usage) <= _USAGE_MAX_KEYS
    _usage.clear()


def test_assistant_never_speaks_in_emoji():
    from app.gemini import (
        _OFFLINE_FREEFORM,
        _OFFLINE_GUIDED,
        GUARDRAILS,
        OFFLINE_NOTE,
        QUOTA_MESSAGE,
    )
    from app.moderation import strip_emoji

    spoken = [OFFLINE_NOTE, QUOTA_MESSAGE, *_OFFLINE_FREEFORM]
    for pool in _OFFLINE_GUIDED.values():
        spoken.extend(pool)
    for line in spoken:
        assert strip_emoji(line) == line, line

    assert "emoji" in GUARDRAILS.lower()


def test_blocked_emoji_input_gets_the_emoji_reply():
    reply, idea = freeform_reply([], "😭😭😭", "t-emoji")
    assert reply == REPLIES["emoji"]
    assert idea is None


def test_crisis_input_never_reaches_the_model():
    reply, idea = freeform_reply([], "em ko muốn sốg nữa", "t-crisis")
    assert reply == REPLIES["crisis"]
    assert idea is None


def test_quota_floors_at_cap():
    _usage.clear()
    key = "het-han-muc"
    from app.config import MAX_MESSAGES_PER_SESSION

    for _ in range(MAX_MESSAGES_PER_SESSION):
        assert _spend(key)
    assert not _spend(key)
    assert quota_left(key) == 0
    _usage.clear()
