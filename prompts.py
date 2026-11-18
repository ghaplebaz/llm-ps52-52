"""Prompts for the prescription reader.

The first prompt returned loose paragraphs, so the table columns changed
from run to run and a missing duration was sometimes filled in. The final
prompt forces one JSON object, maps common Indian timing codes, and leaves
days empty when the prescription does not state them.
"""

PROMPT_CHANGE = (
    "The first prompt asked for a free-text schedule. The model renamed "
    "columns and sometimes invented a duration that was not written. The "
    "final prompt asks for one JSON object, maps codes such as 1-0-1, OD, "
    "BD, TDS and HS onto morning, afternoon and night, and requires days "
    "to be null when no duration is written."
)

SYSTEM_RULES = """You convert prescription text into a medication timetable.
You only copy what is written. You do not add a medicine, a dose, or a duration.
You do not diagnose, and you do not say whether a medicine is safe.
If a line is unreadable, skip that medicine and describe the problem in "unclear".
"""

FINAL_PROMPT = """{rules}

Return only JSON with this shape and no markdown:
{{
  "patient_name": string or null,
  "doctor_name": string or null,
  "date": string or null,
  "medicines": [
    {{
      "medicine": string,
      "dose": string,
      "morning": boolean,
      "afternoon": boolean,
      "night": boolean,
      "days": number or null,
      "instruction": string,
      "frequency_raw": string
    }}
  ],
  "unclear": [string]
}}

The text may be a photo reading of handwriting. Repair only obvious misreads:
- "wg" or "wa" after a number is mg. "wl" or "mul" is ml.
- In a pattern like 1-1-1 or 1-0-1, a 4 is a misread 1.
- "OP" as a frequency means OD, once daily. "BP" as a frequency means BD, twice daily. "TRS" means TDS.
- "xS5days", "x5days", and "x 5 da ys" mean 5 days. If no day count is visible, days is null.
- Do not add a medicine that is not in the text.

Timing rules:
- "1-0-1" style codes are morning-afternoon-night. 1 means that time of day, 0 means skip it.
- OD or once daily: morning is true, unless the text says night, HS, or bedtime.
- BD, BID, or twice daily: morning and night.
- TDS, TID, or three times a day: morning, afternoon, and night.
- QID or four times a day: morning, afternoon, and night, and write "four times a day" in instruction.
- HS, bedtime, or "at night": night only.
- SOS, PRN, or "if needed": morning, afternoon, and night are all false. Put "only if needed" in instruction.
- "x 5 days", "for 5 days", or "× 5/7" means days = 5.
- A weekly or monthly medicine is not a daily slot. Leave morning, afternoon, and night false, set days to null, and keep the weekly or monthly wording in instruction.
- If no duration is written, days must be null. Do not guess a number.
- Copy the dose as written, such as "500 mg" or "5 ml".
- frequency_raw must quote the timing text you used, such as "1-0-1" or "BD".
- Ignore clinic letterhead, registration numbers, and signatures.

Prescription text:
\"\"\"
{prescription}
\"\"\"
"""


def build_prompt(prescription: str) -> str:
    return FINAL_PROMPT.format(rules=SYSTEM_RULES.strip(), prescription=prescription.strip())
