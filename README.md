# Prescription Reader (PS 52)

Handwritten-style prescription text is hard to follow. This app extracts each medicine, its dose, whether it is taken in the morning, afternoon, or night, and for how many days, then shows a timetable.

It gives general information only. It is not medical advice. Confirm every line with a doctor or pharmacist.

## Problem statement

Patients and caregivers lose track of medicine names, timings, and duration when a prescription is written in shorthand (`1-0-1`, `BD`, `TDS`, `OD`, `HS`). The tool turns that text into a clear schedule.

## How to run

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Put a free Gemini API key in `.env` (`GEMINI_API_KEY`). Create one at [Google AI Studio](https://aistudio.google.com/apikey).

```bash
streamlit run app.py
```

The page includes 50 fictional slips. Each one has a text file in `samples/` and a handwritten photo in `samples/photos/`. Pick a slip, or upload your own photo. The reading is shown in the text box so it can be corrected before the schedule is built. Photo reading uses the Tesseract program; on macOS, `brew install tesseract` if the bundled copy is not present.

## What to submit

Upload these into your own Google Drive folder before 11:30 AM on 22 November 2026:

- `Report.pdf` — two-page procedure report (draft in `report/PROCEDURE_REPORT.md`)
- `Code.zip` — this folder, without `.env` and without `venv/`
- `github_link.txt` — the public repository URL
- `screenshots/` — 3 to 5 pictures of the running app

Public repository: [prescription-reader](https://github.com/ghaplebaz/prescription-reader).

Do not commit `.env`. The `.gitignore` file already excludes it.

## Sample inputs

Fifty fictional prescriptions are in `samples/`, numbered 01 to 50. Load any of them from the dropdown and click **Build schedule**. The matching handwritten photo is shown beside the text. They cover short courses, once-daily and weekly medicines, abbreviations, a missing duration, syrups, drops, and messy writing.

Screenshots of real outputs are in `screenshots/`.
