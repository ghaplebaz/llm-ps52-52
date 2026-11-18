"""Call Gemini and turn the JSON into a clean schedule.

The model does the reading. This file checks the shape of the answer and
fills morning / afternoon / night only when the model left them blank but
still quoted a timing code such as 1-0-1.
"""

from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

from dotenv import load_dotenv

from prompts import build_prompt

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

SLOT_PATTERN = re.compile(r"\b([01])\s*[-–]\s*([01])\s*[-–]\s*([01])\b")
WEEKLY_PATTERN = re.compile(r"\b(week|weekly|month|monthly)\b", re.I)


class MissingApiKey(Exception):
    pass


class ModelError(Exception):
    pass


def call_gemini(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise MissingApiKey(
            "GEMINI_API_KEY is missing. Copy .env.example to .env and paste a key from https://aistudio.google.com/apikey"
        )
    model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite").strip() or "gemini-3.5-flash-lite"
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )
    body = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1,
            "responseMimeType": "application/json",
        },
    }
    encoded = json.dumps(body).encode("utf-8")
    payload = None
    for attempt in range(3):
        request = urllib.request.Request(
            url,
            data=encoded,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                payload = json.loads(response.read().decode("utf-8"))
            break
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            if error.code in {429, 503} and attempt < 2:
                time.sleep(2 * (attempt + 1))
                continue
            raise ModelError(f"Gemini returned HTTP {error.code}. {detail[:500]}") from error
        except urllib.error.URLError as error:
            raise ModelError(f"Could not reach Gemini. {error.reason}") from error

    candidates = payload.get("candidates") or []
    if not candidates:
        feedback = payload.get("promptFeedback") or {}
        raise ModelError(f"Gemini returned no text. {feedback}")
    parts = candidates[0].get("content", {}).get("parts") or []
    if not parts or "text" not in parts[0]:
        raise ModelError("Gemini returned an empty response.")
    return parts[0]["text"]


def extract_json(text: str) -> dict:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start < 0 or end <= start:
            raise
        parsed = json.loads(cleaned[start : end + 1])
    if not isinstance(parsed, dict):
        raise json.JSONDecodeError("Top-level JSON must be an object", cleaned, 0)
    return parsed


def _as_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "y", "1"}
    return False


def _as_days(value):
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        days = int(value)
        return days if days > 0 else None
    match = re.search(r"\d+", str(value))
    if not match:
        return None
    days = int(match.group())
    return days if days > 0 else None


def _blank(value) -> str:
    if value is None:
        return ""
    return str(value).strip()


def apply_frequency_fallback(medicine: dict) -> dict:
    """Fill empty time slots from a quoted code. Leave set slots unchanged."""
    if medicine["morning"] or medicine["afternoon"] or medicine["night"]:
        return medicine
    raw = f"{medicine['frequency_raw']} {medicine['instruction']}"
    if WEEKLY_PATTERN.search(raw):
        return medicine
    slot = SLOT_PATTERN.search(raw)
    if slot:
        medicine["morning"] = slot.group(1) == "1"
        medicine["afternoon"] = slot.group(2) == "1"
        medicine["night"] = slot.group(3) == "1"
        return medicine
    lowered = raw.lower()
    if re.search(r"\b(sos|p\.?r\.?n\.?|if needed|as needed|when required)\b", lowered):
        return medicine
    if re.search(r"\b(qid|q\.i\.d\.|four times)\b", lowered):
        medicine["morning"] = medicine["afternoon"] = medicine["night"] = True
        note = "Written as four times a day. Confirm the fourth dose with a pharmacist."
        medicine["instruction"] = f"{medicine['instruction']} {note}".strip()
        return medicine
    if re.search(r"\b(tds|t\.i\.d\.|tid|thrice|three times)\b", lowered):
        medicine["morning"] = medicine["afternoon"] = medicine["night"] = True
        return medicine
    if re.search(r"\b(bd|b\.d\.|bid|b\.i\.d\.|twice)\b", lowered):
        medicine["morning"] = True
        medicine["night"] = True
        return medicine
    if re.search(r"\b(hs|h\.s\.|bedtime|at night)\b", lowered):
        medicine["night"] = True
        return medicine
    if re.search(r"\b(od|o\.d\.|once daily|once a day)\b", lowered):
        medicine["morning"] = True
        return medicine
    return medicine


def normalize_schedule(payload: dict) -> dict:
    medicines = []
    unclear = [_blank(item) for item in payload.get("unclear") or [] if _blank(item)]
    for item in payload.get("medicines") or []:
        if not isinstance(item, dict):
            unclear.append("One medicine entry was not a JSON object and was skipped.")
            continue
        name = _blank(item.get("medicine"))
        if not name:
            unclear.append("A medicine had no name and was skipped.")
            continue
        medicine = {
            "medicine": name,
            "dose": _blank(item.get("dose")) or "not stated",
            "morning": _as_bool(item.get("morning")),
            "afternoon": _as_bool(item.get("afternoon")),
            "night": _as_bool(item.get("night")),
            "days": _as_days(item.get("days")),
            "instruction": _blank(item.get("instruction")),
            "frequency_raw": _blank(item.get("frequency_raw")),
        }
        medicine = apply_frequency_fallback(medicine)
        if medicine["days"] is not None and medicine["days"] > 365:
            unclear.append(
                f"{name}: {medicine['days']} days is unusually long. Check the original text."
            )
        medicines.append(medicine)
    return {
        "patient_name": _blank(payload.get("patient_name")) or None,
        "doctor_name": _blank(payload.get("doctor_name")) or None,
        "date": _blank(payload.get("date")) or None,
        "medicines": medicines,
        "unclear": unclear,
    }


def read_prescription(prescription: str) -> dict:
    text = prescription.strip()
    if not text:
        raise ValueError("Paste a prescription or upload a photo first.")
    if len(text) > 8000:
        raise ValueError("This text is longer than 8000 characters. Paste one prescription at a time.")
    prompt = build_prompt(text)
    raw = call_gemini(prompt)
    try:
        payload = extract_json(raw)
    except json.JSONDecodeError:
        repair = (
            "Convert the following into the JSON object you were asked for. "
            "Return JSON only.\n\n"
            + raw
        )
        raw = call_gemini(repair)
        payload = extract_json(raw)
    schedule = normalize_schedule(payload)
    schedule["prompt"] = prompt
    return schedule


def schedule_rows(schedule: dict) -> list[dict]:
    rows = []
    for medicine in schedule["medicines"]:
        rows.append(
            {
                "Medicine": medicine["medicine"],
                "Dose": medicine["dose"],
                "Morning": "Yes" if medicine["morning"] else "—",
                "Afternoon": "Yes" if medicine["afternoon"] else "—",
                "Night": "Yes" if medicine["night"] else "—",
                "Days": medicine["days"] if medicine["days"] is not None else "not stated",
                "Instruction": medicine["instruction"] or "—",
            }
        )
    return rows


def medicines_for_slot(schedule: dict, slot: str) -> list[dict]:
    return [medicine for medicine in schedule["medicines"] if medicine[slot]]


def only_if_needed(schedule: dict) -> list[dict]:
    kept = []
    for medicine in schedule["medicines"]:
        if medicine["morning"] or medicine["afternoon"] or medicine["night"]:
            continue
        kept.append(medicine)
    return kept
