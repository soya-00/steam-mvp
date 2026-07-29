from __future__ import annotations

import pytest

from app.config import STEAM_FIELDS
from app.scenarios import STAGE_ORDER, ScenarioError, _parse_scenario, all_scenarios


def test_five_fields_all_covered():
    fields = {s.field for s in all_scenarios()}
    assert fields == {f["name"] for f in STEAM_FIELDS}


def test_every_scenario_carries_career_identity():
    for s in all_scenarios():
        assert s.role, s.id
        assert s.protagonist, s.id
        assert s.creation_output, s.id
        assert s.domain_skills, s.id
        assert isinstance(s.has_female_protagonist, bool)


def test_stages_are_canonical_and_ordered():
    for s in all_scenarios():
        keys = [st.key for st in s.stages]
        assert keys == list(STAGE_ORDER), s.id
        for st in s.stages:
            assert st.beats, (s.id, st.key)
        assert s.total_questions >= 12, s.id


def test_loader_fails_loudly_on_malformed_data():
    with pytest.raises(ScenarioError):
        _parse_scenario({"id": "hong", "field": "Toán"}, "test")
    with pytest.raises(ScenarioError):
        _parse_scenario(
            {"id": "hong", "field": "Toán", "title": "x", "stages": [
                {"key": "khong-ton-tai", "beats": [{"type": "context", "text": "x"}]}
            ]},
            "test",
        )
