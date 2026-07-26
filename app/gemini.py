"""Tích hợp Gemini — toàn bộ lời gọi nằm ở phía máy chủ.

Khoá API không bao giờ được gửi xuống trình duyệt. Khi chưa cấu hình khoá,
mọi hàm ở đây rơi về "chế độ demo ngoại tuyến": trả lời bằng kịch bản dựng
sẵn để mọi màn hình vẫn bấm được, và giao diện hiển thị rõ điều đó.
"""

from __future__ import annotations

import logging
import re
import threading

from app.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GEMINI_MODEL_PREFERENCE,
    MAX_MESSAGES_PER_SESSION,
    gemini_enabled,
)

log = logging.getLogger("gals.gemini")

IDEA_TAG = "[[Ý_TƯỞNG]]"

_client = None
_model: str | None = None
_lock = threading.Lock()

# Trần số lượt cho mỗi phiên — demo chạy trên URL công khai lúc chấm thi.
_usage: dict[str, int] = {}


# --------------------------------------------------------------------------
# Rào an toàn dùng chung cho mọi lời nhắc hệ thống
# --------------------------------------------------------------------------

GUARDRAILS = """
NGUYÊN TẮC BẮT BUỘC — áp dụng cho mọi câu trả lời:
- Luôn trả lời bằng tiếng Việt, giọng ấm áp, khích lệ, phù hợp với học sinh THPT.
- Người dùng là trẻ vị thành niên. Không bao giờ hỏi thông tin liên lạc cá nhân
  (tên trường, địa chỉ, số điện thoại, mạng xã hội) và không đề nghị gặp mặt.
- Không đưa lời khuyên y tế, pháp lý hay tâm lý. Nếu học sinh nhắc tới chuyện
  sức khoẻ, an toàn hoặc tinh thần của chính mình, hãy nhẹ nhàng khuyên em nói
  với một người lớn đáng tin cậy (thầy cô, bố mẹ, người thân), rồi quay lại
  chủ đề đang thảo luận. Không phân tích, không chẩn đoán.
- Nếu cuộc trò chuyện lệch sang chủ đề không phù hợp, đừng phê phán em. Chuyển
  hướng nhẹ nhàng về tình huống nghề nghiệp đang bàn.
- KHÔNG BAO GIỜ chấm điểm, xếp loại, so sánh em với người khác, hay nói "đáp án
  đúng là...". Sản phẩm này cố tình không có điểm số.
- Không củng cố định kiến giới về nghề nghiệp. Mọi lĩnh vực STEAM đều mở với
  mọi học sinh. Đừng bao giờ ám chỉ ai đó hợp hay không hợp với một nghề vì
  giới tính của họ.
- Viết ngắn. Tối đa 4-5 câu, trừ khi được yêu cầu tổng hợp.
"""


def _guided_system(scenario, stage) -> str:
    skills = ", ".join(scenario.domain_skills) if scenario.domain_skills else ""
    return f"""
Bạn là người đồng hành tư duy cho một học sinh THPT Việt Nam đang nhập vai
"{scenario.role}" trong tình huống "{scenario.title}".

Em ấy đang ở cấp độ "{stage.name}" của quy trình tư duy thiết kế.
Chuyên môn mà tình huống này cần dùng: {skills}.
Ở cấp độ Sáng tạo, sản phẩm em cần tạo ra là: {scenario.creation_output}.

CÁCH PHẢN HỒI:
1. Nhắc lại thật ngắn điều đáng chú ý trong câu trả lời của em — cụ thể, không khen chung chung.
2. Đặt MỘT câu hỏi đào sâu, bằng ngôn ngữ đời thường.
3. Dừng lại. Đừng trả lời thay em, đừng đưa ra kết luận của tình huống.

Nếu em bỏ sót một điều quan trọng, đừng nói thẳng ra. Hãy hỏi một câu khiến em
tự nhận ra.

Bạn có thể mượn các lăng kính sau, nhưng KHÔNG được gọi tên chúng và không
giảng lý thuyết — chỉ diễn đạt thành câu hỏi ngắn, dễ hiểu:
- Nguyên lý đầu tiên: "Điều gì ở đây bạn biết chắc, và điều gì bạn đang giả định?"
- Phân tích bên liên quan: "Ai còn chịu ảnh hưởng mà chưa được nhắc tới?"
- SCAMPER: "Nếu bỏ bớt hoặc đổi một phần thì sao?"

QUAN TRỌNG NHẤT: mỗi nghề thu thập bằng chứng và ra quyết định theo cách riêng.
Hãy hỏi theo đúng cách một {scenario.role} suy nghĩ — về dữ liệu, ràng buộc và
bằng chứng của nghề đó. Tuyệt đối không quy mọi thứ về "phỏng vấn người dùng
rồi thiết kế ứng dụng".
{GUARDRAILS}
""".strip()


FREEFORM_SYSTEM = f"""
Bạn là người bạn đồng hành giúp một học sinh THPT Việt Nam nghĩ thành lời.

Không có khung sườn, không có bước bắt buộc. Em có thể kể về điều em để ý thấy,
điều làm em khó chịu, một thắc mắc vu vơ, hay một ý tưởng còn dở dang.

CÁCH TRÒ CHUYỆN:
- Tò mò thật sự. Hỏi thêm về điều em vừa nói trước khi đưa ra bất cứ gợi ý nào.
- Mỗi lượt chỉ hỏi MỘT câu.
- Nếu em nói "em không biết" hoặc "em chưa nghĩ ra", đừng ép. Hỏi một câu dễ hơn,
  cụ thể hơn, gắn với đời sống hằng ngày của em.
- Đừng vội biến mọi thứ thành dự án. Đôi khi nghĩ vẩn vơ đã là đủ.

KHI NHẬN RA MỘT Ý ĐÁNG GIỮ:
Nếu em vừa nói ra điều gì đó thật sự là một ý tưởng hoặc một quan sát sắc sảo,
hãy kết thúc lượt trả lời bằng MỘT dòng riêng theo đúng định dạng:
{IDEA_TAG} <tóm tắt ý tưởng trong một câu>

Chỉ làm điều này khi thật sự có ý đáng giữ, nhiều nhất một lần mỗi vài lượt.
Bạn KHÔNG có quyền tự thêm gì vào hồ sơ của em — dòng đó chỉ để hệ thống hiện
một nút hỏi ý em. Quyền quyết định luôn thuộc về em.
{GUARDRAILS}
""".strip()


def _synthesis_system(scenario) -> str:
    return f"""
Học sinh vừa đi hết bốn cấp độ tư duy trong tình huống "{scenario.title}",
nhập vai {scenario.role}.

Hãy viết một đoạn nhìn lại hành trình của em, dựa HOÀN TOÀN vào những gì chính
em đã viết. Không thêm ý em chưa từng nói.

Đi qua năm điều sau, mỗi điều 1-2 câu, viết liền mạch như đang nói chuyện với em:
1. Cách em đọc và diễn giải dữ liệu.
2. Những giả định em đã tự nhận ra.
3. Các bên liên quan và góc nhìn em đã cân nhắc.
4. Sự đánh đổi trong hướng giải quyết của em.
5. Những điều em vẫn còn chưa chắc chắn.

TUYỆT ĐỐI KHÔNG: chấm điểm, xếp loại, nói em đúng hay sai, hay đưa ra "đáp án
mẫu" của tình huống. Chỗ em còn chưa chắc chắn là điều đáng quý, không phải
thiếu sót — hãy nói với em như vậy.
{GUARDRAILS}
""".strip()


# --------------------------------------------------------------------------
# Kết nối và chọn model
# --------------------------------------------------------------------------


def get_client():
    global _client
    if not gemini_enabled():
        return None
    with _lock:
        if _client is None:
            from google import genai

            _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


def resolve_model() -> str:
    """Chọn model flash hiện hành.

    Không hard-code tên model theo trí nhớ: hỏi thẳng API xem có gì, rồi lấy
    lựa chọn khả dụng đầu tiên theo thứ tự ưu tiên. Biến GEMINI_MODEL ghi đè.
    """
    global _model
    if _model:
        return _model
    if GEMINI_MODEL:
        _model = GEMINI_MODEL
        return _model

    client = get_client()
    if client is None:
        _model = GEMINI_MODEL_PREFERENCE[0]
        return _model

    try:
        available = set()
        for m in client.models.list():
            name = (m.name or "").removeprefix("models/")
            actions = m.supported_actions or []
            if not actions or "generateContent" in actions:
                available.add(name)

        for candidate in GEMINI_MODEL_PREFERENCE:
            if candidate in available:
                _model = candidate
                log.info("Gemini: chọn model %s", _model)
                return _model

        flash = sorted(n for n in available if "flash" in n and "preview" not in n)
        if flash:
            _model = flash[-1]
            log.warning("Gemini: không thấy model ưu tiên, dùng %s", _model)
            return _model
    except Exception as exc:  # pragma: no cover - phụ thuộc mạng
        log.warning("Gemini: không liệt kê được model (%s), dùng mặc định", exc)

    _model = GEMINI_MODEL_PREFERENCE[0]
    return _model


# --------------------------------------------------------------------------
# Trần số lượt
# --------------------------------------------------------------------------


def quota_left(session_key: str) -> int:
    return max(0, MAX_MESSAGES_PER_SESSION - _usage.get(session_key, 0))


def _spend(session_key: str) -> bool:
    used = _usage.get(session_key, 0)
    if used >= MAX_MESSAGES_PER_SESSION:
        return False
    _usage[session_key] = used + 1
    return True


QUOTA_MESSAGE = (
    "Phiên demo này đã dùng hết số lượt trò chuyện. Bạn vẫn xem lại được toàn bộ "
    "nhật ký và hồ sơ của mình — chỉ phần trò chuyện tạm dừng thôi."
)


# --------------------------------------------------------------------------
# Gọi model
# --------------------------------------------------------------------------


def _generate(system: str, contents: list[dict], *, max_tokens: int = 600) -> str | None:
    client = get_client()
    if client is None:
        return None
    from google.genai import types

    try:
        resp = client.models.generate_content(
            model=resolve_model(),
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system,
                temperature=0.85,
                max_output_tokens=max_tokens,
            ),
        )
        text = (resp.text or "").strip()
        return text or None
    except Exception as exc:  # pragma: no cover - phụ thuộc mạng
        log.warning("Gemini: lời gọi thất bại (%s)", exc)
        return None


def _turns(history: list[dict]) -> list[dict]:
    return [
        {"role": "model" if h["role"] == "ai" else "user", "parts": [{"text": h["text"]}]}
        for h in history
    ]


# --------------------------------------------------------------------------
# Kịch bản dự phòng khi chạy ngoại tuyến
# --------------------------------------------------------------------------

_OFFLINE_GUIDED = {
    "hieu_van_de": [
        "Mình ghi nhận cách bạn đọc dữ kiện. Trong những điều bạn vừa nêu, đâu là thứ bạn "
        "biết chắc, và đâu là thứ bạn đang suy đoán?",
        "Bạn đang dựa vào con số nào để nói vậy? Nếu con số đó được thu thập theo cách khác, "
        "kết luận của bạn có đổi không?",
    ],
    "dong_cam": [
        "Bạn đã nghĩ tới một bên liên quan rồi. Còn ai chịu ảnh hưởng mà chưa được nhắc tới "
        "trong câu trả lời của bạn?",
        "Nếu người đó nghe được điều bạn vừa viết, bạn nghĩ họ sẽ phản ứng thế nào?",
    ],
    "sang_tao": [
        "Hướng của bạn nghe hợp lý. Nó đang dựa trên giả định nào về cách mọi người thật sự "
        "làm việc hằng ngày?",
        "Nếu phải bỏ bớt một phần trong đề xuất này, bạn sẽ bỏ phần nào, và mất gì khi bỏ?",
    ],
    "phan_chieu": [
        "Bạn đang diễn giải kết quả theo một hướng. Có cách giải thích nào khác cũng khớp với "
        "chính những số liệu đó không?",
        "Điều gì sẽ khiến bạn thay đổi kết luận của mình?",
    ],
}

_OFFLINE_FREEFORM = [
    "Chỗ đó nghe thú vị đấy. Bạn kể thêm xem lần gần nhất bạn thấy chuyện này là khi nào?",
    "Mình tò mò — điều gì khiến bạn để ý tới chuyện này chứ không phải chuyện khác?",
    "Nếu bạn được thay đổi một thứ duy nhất trong tình huống đó, bạn sẽ đổi gì?",
    "Bạn nghĩ ai là người bị ảnh hưởng nhiều nhất mà ít ai để ý tới?",
]

OFFLINE_NOTE = "Đang chạy ở chế độ demo ngoại tuyến — câu trả lời này lấy từ kịch bản dựng sẵn."


def _offline_guided(stage_key: str, turn: int) -> str:
    pool = _OFFLINE_GUIDED.get(stage_key) or _OFFLINE_GUIDED["hieu_van_de"]
    return pool[turn % len(pool)]


def _offline_freeform(turn: int, message: str = "") -> tuple[str, str | None]:
    """Ở chế độ ngoại tuyến vẫn thỉnh thoảng đề nghị lưu ý tưởng.

    Đây là điểm đặc trưng nhất của chế độ tự do, nên nếu bỏ qua thì lúc chấm
    thi sẽ không ai nhìn thấy nó. Ý tưởng lấy từ chính lời học sinh vừa viết,
    và vẫn phải được em bấm đồng ý mới lưu.
    """
    reply = _OFFLINE_FREEFORM[turn % len(_OFFLINE_FREEFORM)]
    idea = None
    cleaned = " ".join(message.split())
    if turn % 2 == 1 and len(cleaned) >= 25:
        idea = cleaned[:160].rstrip(" ,.;") + ("…" if len(cleaned) > 160 else "")
    return reply, idea


def _offline_synthesis(scenario, answers: list[str]) -> str:
    n = len(answers)
    return (
        f"Bạn đã đi hết bốn cấp độ trong vai {scenario.role} và để lại {n} câu trả lời. "
        "Nhìn lại, bạn đã đọc dữ liệu thay vì tin ngay vào lời giải thích có sẵn, và ở vài "
        "chỗ bạn đã tự nêu ra điều mình chưa chắc chắn — đó chính là cách người làm nghề "
        "này suy nghĩ. Những câu bạn còn để ngỏ không phải là chỗ thiếu, mà là chỗ đáng "
        "quay lại khi có thêm dữ kiện. "
        + OFFLINE_NOTE
    )


# --------------------------------------------------------------------------
# API cho router
# --------------------------------------------------------------------------


def guided_reply(scenario, stage, question: str, answer: str, turn: int, session_key: str) -> str:
    """Phản hồi ngắn cho một câu trả lời trong Không gian tư duy."""
    if not gemini_enabled():
        return _offline_guided(stage.key, turn)
    if not _spend(session_key):
        return QUOTA_MESSAGE

    text = _generate(
        _guided_system(scenario, stage),
        [
            {
                "role": "user",
                "parts": [
                    {
                        "text": (
                            f"Câu hỏi em vừa được hỏi:\n{question}\n\n"
                            f"Câu trả lời của em:\n{answer}"
                        )
                    }
                ],
            }
        ],
        max_tokens=400,
    )
    return text or _offline_guided(stage.key, turn)


def freeform_reply(history: list[dict], message: str, session_key: str) -> tuple[str, str | None]:
    """Trả về (lời đáp, ý tưởng gợi lưu hoặc None)."""
    turn = len(history) // 2
    if not gemini_enabled():
        return _offline_freeform(turn, message)
    if not _spend(session_key):
        return QUOTA_MESSAGE, None

    contents = _turns(history) + [{"role": "user", "parts": [{"text": message}]}]
    text = _generate(FREEFORM_SYSTEM, contents, max_tokens=500)
    if not text:
        return _offline_freeform(turn, message)

    return split_idea(text)


def split_idea(text: str) -> tuple[str, str | None]:
    """Tách dòng sentinel ra khỏi lời đáp hiển thị cho học sinh.

    Sentinel chỉ là tín hiệu để hiện nút hỏi ý — không bao giờ tự lưu.
    """
    pattern = re.escape(IDEA_TAG) + r"\s*(.+)"
    match = re.search(pattern, text)
    if not match:
        return text.strip(), None
    idea = match.group(1).strip().strip("<>").strip()
    cleaned = re.sub(pattern, "", text).strip()
    return cleaned, (idea or None)


def synthesis(scenario, transcript: list[dict], session_key: str) -> str:
    """Phần "Kết thúc flow": tổng hợp lại hành trình, không điểm số, không đáp án mẫu."""
    answers = [t for t in transcript if t.get("answer")]
    if not gemini_enabled():
        return _offline_synthesis(scenario, [a["answer"] for a in answers])
    if not _spend(session_key):
        return _offline_synthesis(scenario, [a["answer"] for a in answers])

    body = "\n\n".join(
        f"[{t.get('stage', '')}] {t.get('label', '')}\nHỏi: {t.get('text', '')}\n"
        f"Em trả lời: {t['answer']}"
        for t in answers
    )
    text = _generate(
        _synthesis_system(scenario),
        [{"role": "user", "parts": [{"text": body}]}],
        max_tokens=900,
    )
    return text or _offline_synthesis(scenario, [a["answer"] for a in answers])
