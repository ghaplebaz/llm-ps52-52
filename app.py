"""Prescription Reader — problem statement 52.

Paste a prescription, or upload a photo and correct the OCR text.
Gemini returns each medicine, dose, morning / afternoon / night, and days.
The screen only organises those words. It does not give medical advice.
"""

from __future__ import annotations

import csv
import html
import io
from pathlib import Path

import streamlit as st

from extractor import (
    MissingApiKey,
    ModelError,
    medicines_for_slot,
    only_if_needed,
    read_prescription,
    schedule_rows,
)
from ocr_utils import OcrUnavailable, read_image
from prompts import PROMPT_CHANGE

ROOT = Path(__file__).resolve().parent
SAMPLES = sorted((ROOT / "samples").glob("*.txt"))

DISCLAIMER = (
    "This is not medical advice. The app only turns the words in a prescription "
    "into a timetable. It can misread a medicine, a dose, or a number of days. "
    "Check every line with a doctor or pharmacist before taking any medicine."
)

st.set_page_config(page_title="Prescription Reader", page_icon="Rx", layout="wide")
st.markdown(
    """
    <style>
    .block-container { max-width: 1080px; padding-top: 1.5rem; }
    .disclaimer {
        background: #fff6e8;
        border: 1px solid #e4c48a;
        border-left: 6px solid #9a3412;
        color: #431407;
        border-radius: 10px;
        padding: 0.85rem 1rem;
        margin: 0.4rem 0 1rem 0;
        line-height: 1.45;
    }
    .slot-card {
        background: #f4f7f5;
        border: 1px solid #d5e0d8;
        border-radius: 12px;
        padding: 0.8rem 0.9rem 0.4rem 0.9rem;
        min-height: 180px;
    }
    .slot-card h4 { margin: 0 0 0.6rem 0; color: #1f3d32; white-space: nowrap; }
    .med-line { margin: 0 0 0.75rem 0; }
    .med-line strong { color: #14261f; display: block; }
    .med-line span { display: block; color: #3f5349; font-size: 0.92rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


def load_sample(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def rows_to_csv(rows: list[dict]) -> str:
    buffer = io.StringIO()
    if not rows:
        return ""
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def render_slot(title: str, medicines: list[dict]) -> None:
    lines = []
    if not medicines:
        lines.append("<p class='med-line'><span>Nothing scheduled.</span></p>")
    for medicine in medicines:
        days = f"{medicine['days']} days" if medicine["days"] is not None else "duration not stated"
        instruction = medicine["instruction"] or "no extra instruction"
        lines.append(
            "<p class='med-line'>"
            f"<strong>{html.escape(medicine['medicine'])}</strong>"
            f"<span>{html.escape(medicine['dose'])} · {html.escape(days)}</span>"
            f"<span>{html.escape(instruction)}</span>"
            "</p>"
        )
    st.markdown(
        f"<div class='slot-card'><h4>{title}</h4>{''.join(lines)}</div>",
        unsafe_allow_html=True,
    )


st.title("Prescription Reader")
st.caption("Problem statement 52 · roll number 52 · 50 fictional slips · informational timetable only")
st.markdown(f"<div class='disclaimer'>{DISCLAIMER}</div>", unsafe_allow_html=True)

if "prescription_text" not in st.session_state:
    st.session_state.prescription_text = load_sample(SAMPLES[0]) if SAMPLES else ""
if "schedule" not in st.session_state:
    st.session_state.schedule = None
if "form_error" not in st.session_state:
    st.session_state.form_error = None

st.subheader("Prescription")
mode = st.radio("Input", ["Paste text", "Photo (OCR)"], horizontal=True)
labels = [f"{index + 1:02d} · {path.stem.split('_', 1)[-1].replace('_', ' ')}" for index, path in enumerate(SAMPLES)]
picked = st.selectbox("Sample prescriptions (50)", labels, index=0)
sample = SAMPLES[labels.index(picked)] if labels else None
if sample is not None and st.session_state.get("loaded_sample") != sample.name:
    st.session_state.prescription_text = load_sample(sample)
    st.session_state.loaded_sample = sample.name
    st.session_state.schedule = None
    st.session_state.form_error = None

text_col, photo_col = st.columns([1.15, 0.85], gap="large")
with text_col:
    if mode == "Photo (OCR)":
        upload = st.file_uploader("Handwritten prescription photo", type=["png", "jpg", "jpeg", "webp"])
        if upload is not None and st.button("Read text from photo"):
            try:
                st.session_state.prescription_text = read_image(upload)
                st.session_state.loaded_sample = None
                st.session_state.schedule = None
            except OcrUnavailable as error:
                st.error(str(error))
        st.caption("Check the reading below. Handwriting is often misread.")
    st.text_area(
        "Prescription text",
        key="prescription_text",
        height=260,
        placeholder="Paste the prescription here, or read it from a photo.",
    )
    build = st.button("Build schedule", type="primary")
with photo_col:
    photo = ROOT / "samples" / "photos" / f"{sample.stem}.png" if sample is not None else None
    if photo is not None and photo.exists():
        st.image(str(photo), caption="Handwritten slip for this sample", use_container_width=True)
    else:
        st.caption("Upload a photo on the left, or pick one of the 50 samples.")

st.subheader("Schedule")
if build:
    try:
        with st.spinner("Reading the prescription…"):
            st.session_state.schedule = read_prescription(st.session_state.prescription_text)
        st.session_state.form_error = None
    except (MissingApiKey, ModelError, ValueError) as error:
        st.session_state.schedule = None
        st.session_state.form_error = str(error)
    except Exception as error:
        st.session_state.schedule = None
        st.session_state.form_error = str(error)

schedule = st.session_state.schedule
if st.session_state.form_error:
    st.error(st.session_state.form_error)
elif schedule is None:
    st.info("Choose a sample or paste a prescription, then click Build schedule.")
elif not schedule["medicines"]:
    st.warning("No medicines were found. Check the text and try again.")
    for note in schedule["unclear"]:
        st.write(f"- {note}")
else:
    bits = []
    if schedule["patient_name"]:
        bits.append(f"Patient: {schedule['patient_name']}")
    if schedule["doctor_name"]:
        bits.append(f"Doctor: {schedule['doctor_name']}")
    if schedule["date"]:
        bits.append(f"Date: {schedule['date']}")
    if bits:
        st.caption(" · ".join(bits))

    morning, afternoon, night = st.columns(3)
    with morning:
        render_slot("Morning", medicines_for_slot(schedule, "morning"))
    with afternoon:
        render_slot("Afternoon", medicines_for_slot(schedule, "afternoon"))
    with night:
        render_slot("Night", medicines_for_slot(schedule, "night"))

    as_needed = only_if_needed(schedule)
    if as_needed:
        st.markdown("**Not on a fixed clock**")
        for medicine in as_needed:
            st.write(
                f"{medicine['medicine']} · {medicine['dose']} · "
                f"{medicine['instruction'] or medicine['frequency_raw'] or 'timing not stated'}"
            )

    rows = schedule_rows(schedule)
    st.dataframe(rows, use_container_width=True, hide_index=True)
    st.download_button(
        "Download CSV",
        data=rows_to_csv(rows),
        file_name="prescription_schedule.csv",
        mime="text/csv",
        use_container_width=True,
    )
    if schedule["unclear"]:
        st.warning("Check these lines against the original slip.")
        for note in schedule["unclear"]:
            st.write(f"- {note}")

with st.expander("Prompt used in this app"):
    st.write(PROMPT_CHANGE)
    if st.session_state.schedule and st.session_state.schedule.get("prompt"):
        st.code(st.session_state.schedule["prompt"], language="text")
    else:
        st.caption("Build a schedule to see the exact prompt sent for that prescription.")
