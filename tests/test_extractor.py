import json

import pytest

from extractor import (
    apply_frequency_fallback,
    extract_json,
    medicines_for_slot,
    normalize_schedule,
    only_if_needed,
    schedule_rows,
)
from prompts import PROMPT_CHANGE, build_prompt


def _medicine(**overrides):
    medicine = {
        "medicine": "Paracetamol",
        "dose": "650 mg",
        "morning": False,
        "afternoon": False,
        "night": False,
        "days": 3,
        "instruction": "",
        "frequency_raw": "",
    }
    medicine.update(overrides)
    return medicine


def test_prompt_locks_the_json_shape_and_forbids_guessing():
    prompt = build_prompt("Tab Paracetamol 650 mg 1-0-1 x 3 days")
    assert '"days": number or null' in prompt
    assert "Do not guess a number." in prompt
    assert "1-0-1" in prompt
    assert "free-text" in PROMPT_CHANGE


def test_extract_json_strips_fences_and_extra_words():
    raw = 'Here is the schedule:\n```json\n{"medicines": [], "unclear": []}\n```'
    assert extract_json(raw)["medicines"] == []


def test_slot_code_fills_blank_times():
    medicine = apply_frequency_fallback(_medicine(frequency_raw="1-0-1"))
    assert medicine["morning"] is True
    assert medicine["afternoon"] is False
    assert medicine["night"] is True


def test_existing_times_are_not_overwritten():
    medicine = apply_frequency_fallback(
        _medicine(morning=True, frequency_raw="0-0-1")
    )
    assert medicine["morning"] is True
    assert medicine["night"] is False


def test_abbreviations_and_weekly_and_sos():
    twice = apply_frequency_fallback(_medicine(frequency_raw="BD"))
    assert (twice["morning"], twice["afternoon"], twice["night"]) == (True, False, True)
    thrice = apply_frequency_fallback(_medicine(frequency_raw="TDS"))
    assert (thrice["morning"], thrice["afternoon"], thrice["night"]) == (True, True, True)
    night = apply_frequency_fallback(_medicine(frequency_raw="HS"))
    assert (night["morning"], night["night"]) == (False, True)
    weekly = apply_frequency_fallback(_medicine(frequency_raw="once weekly"))
    assert weekly["morning"] is False
    sos = apply_frequency_fallback(_medicine(frequency_raw="SOS"))
    assert sos["morning"] is False and sos["night"] is False


def test_normalize_skips_blank_names_and_keeps_missing_days():
    schedule = normalize_schedule(
        {
            "patient_name": "  R. Deshmukh ",
            "medicines": [
                {
                    "medicine": "Ibuprofen",
                    "dose": "400 mg",
                    "morning": "yes",
                    "afternoon": 0,
                    "night": "1",
                    "days": "not written",
                    "instruction": "after food",
                    "frequency_raw": "1-0-1",
                },
                {"medicine": "  ", "dose": "10 mg"},
            ],
            "unclear": ["", "smudged line"],
        }
    )
    assert schedule["patient_name"] == "R. Deshmukh"
    assert len(schedule["medicines"]) == 1
    assert schedule["medicines"][0]["days"] is None
    assert schedule["medicines"][0]["morning"] is True
    assert schedule["unclear"] == ["smudged line", "A medicine had no name and was skipped."]
    rows = schedule_rows(schedule)
    assert rows[0]["Days"] == "not stated"
    assert rows[0]["Afternoon"] == "—"


def test_schedule_groups():
    schedule = normalize_schedule(
        {
            "medicines": [
                {
                    "medicine": "Cetirizine",
                    "dose": "10 mg",
                    "night": True,
                    "days": 7,
                    "frequency_raw": "HS",
                },
                {
                    "medicine": "Alprazolam",
                    "dose": "0.25 mg",
                    "frequency_raw": "SOS",
                    "instruction": "only if needed",
                },
            ]
        }
    )
    assert [item["medicine"] for item in medicines_for_slot(schedule, "night")] == ["Cetirizine"]
    assert [item["medicine"] for item in only_if_needed(schedule)] == ["Alprazolam"]


def test_extract_json_rejects_a_list():
    with pytest.raises(json.JSONDecodeError):
        extract_json("[1, 2, 3]")
