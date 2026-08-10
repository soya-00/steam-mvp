from __future__ import annotations

from app.scenarios import STAGE_HINTS, all_scenarios
from tests.conftest import login_independent

COMPOSER = 'name="tra_loi"'
DONE = "đã đi hết bốn cấp độ"


def test_only_one_question_is_on_screen_at_a_time(client):
    login_independent(client)
    for scenario in all_scenarios():
        url = f"/du-an/{scenario.id}/khong-gian-tu-duy"
        for _ in range(250):
            page = client.get(url).text
            if DONE in page.lower():
                break
            assert page.count(COMPOSER) == 1, scenario.id
            client.post(
                f"/du-an/{scenario.id}/tiep",
                data={"tra_loi": "Em chưa chắc, cần thêm dữ liệu để so sánh."},
            )
        else:
            raise AssertionError(f"{scenario.id}: không kết thúc")


def test_narration_never_becomes_a_step_of_its_own(client):
    login_independent(client)
    scenario = all_scenarios()[0]
    url = f"/du-an/{scenario.id}/khong-gian-tu-duy"
    for _ in range(250):
        page = client.get(url).text
        if DONE in page.lower():
            break
        # Nhịp kể chuyện được gom vào cột dữ kiện, không còn nút "đọc xong".
        assert "Tôi đã đọc xong" not in page
        client.post(f"/du-an/{scenario.id}/tiep", data={"tra_loi": "Em nghĩ là chưa đủ."})


def test_narration_shows_up_as_summarised_data_in_the_side_rail(client):
    login_independent(client)
    scenario = all_scenarios()[0]
    opening = next(b for b in scenario.stages[0].beats if b.type == "context")
    page = client.get(f"/du-an/{scenario.id}/khong-gian-tu-duy").text

    assert "Dữ kiện" in page
    # Cột dữ kiện dẫn bằng bản tóm tắt…
    for fact in opening.facts:
        assert fact in page, fact
    # …nguyên văn vẫn đọc lại được, nhưng phải mở ra.
    assert "Đọc nguyên văn bối cảnh" in page


def test_every_context_beat_carries_a_short_summary():
    for scenario in all_scenarios():
        for stage in scenario.stages:
            for beat in stage.beats:
                where = f"{scenario.id} · {stage.key} · {beat.label}"
                if beat.type != "context":
                    continue
                assert beat.facts, where
                for fact in beat.facts:
                    assert len(fact) <= 140, (where, len(fact), fact)
                    assert fact != beat.text, where
                joined = " ".join(beat.facts)
                assert len(joined) < len(beat.text), where


def test_answered_questions_stay_reachable_from_the_side_nav(client):
    login_independent(client)
    scenario = all_scenarios()[0]
    url = f"/du-an/{scenario.id}/khong-gian-tu-duy"
    first_question = client.get(url).text

    client.post(f"/du-an/{scenario.id}/tiep", data={"tra_loi": "Câu trả lời đầu tiên của em."})
    after = client.get(url).text

    assert "Câu đã trả lời (1)" in after
    assert "Câu trả lời đầu tiên của em." in after
    # Câu cũ rời khỏi vị trí câu hỏi chính nhưng vẫn đọc lại được.
    assert after.count(COMPOSER) == 1
    assert first_question != after


def test_hints_are_questions_not_answers(client):
    login_independent(client)
    scenario = all_scenarios()[0]
    page = client.get(f"/du-an/{scenario.id}/khong-gian-tu-duy").text
    assert "Xem gợi ý dẫn dắt" in page

    assert set(STAGE_HINTS) == {s.key for s in scenario.stages}

    for stage_key, hints in STAGE_HINTS.items():
        assert len(hints) == 3, stage_key
        for hint in hints:
            for banned in ["đáp án", "câu trả lời đúng", "bạn nên trả lời", "gợi ý là"]:
                assert banned not in hint.lower(), (stage_key, hint)
            # Gợi ý dùng chung cho cả năm tình huống nên không được nhắc số liệu
            # của riêng tình huống nào.
            assert not any(ch.isdigit() for ch in hint), (stage_key, hint)
