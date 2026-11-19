# Prescription Reader

**Project title:** Prescription Reader
**Problem statement:** 52 - Prescription Reader
**Name:** Rushikesh Wankhede
**Roll number:** 52
**Class:** LYAIA7
**GitHub link:** https://github.com/ghaplebaz/prescription-reader

## Problem statement

Handwritten prescriptions use codes such as 1-0-1, BD and HS, so the time of day is easy to mix up. This project turns the slip into a timetable of medicine, dose, morning, afternoon, night and days. It helps a patient follow a prescription they already have, and it is not medical advice.

## Tools and model

I used Python and Streamlit for the page. Photo reading uses Pillow and pytesseract. The model is Gemini 3.5 Flash Lite through the Gemini API (`gemini-3.5-flash-lite`). The key stays in a local `.env` file and is not uploaded. I did not train a model. Gemini 2.5 Flash was not available on a new key, so this is the model that answered.

## Procedure

1. I matched roll number 52 to problem statement 52, Prescription Reader.
2. I created a Gemini API key and saved it only in `.env`.
3. My first prompt asked for a free-text schedule. The columns changed between runs, and a missing duration was sometimes filled in.
4. I rewrote the prompt so the answer is one JSON object, and days stay empty when the slip does not state a duration.
5. I built the page and 50 fictional slips. Each slip has typed text and a handwritten-style photo.
6. I tested pasted text and photo reading. Text read from a photo is shown in a box so it can be corrected before the timetable is built.

## Prompt used

The change that improved it: the first prompt asked for free text, so the model renamed columns and sometimes invented a duration. The final prompt asks for JSON and forbids a guessed number of days.

Final prompt sent to the model:

You convert prescription text into a medication timetable. You only copy what is written. You do not add a medicine, a dose, or a duration. Return only JSON with patient_name, doctor_name, date, medicines and unclear. Each medicine has medicine, dose, morning, afternoon, night, days, instruction and frequency_raw. A code such as 1-0-1 is morning, afternoon and night. OD is morning, BD is morning and night, TDS is all three, and HS is night only. SOS is not placed on the daily clock; the instruction is "only if needed". If no duration is written, days is null. Do not guess a number.

## Results

Sample 01 is an antibiotic course. The input is the typed slip beside the handwritten photo. The output places Amoxicillin 500 mg morning, afternoon and night for 5 days, Paracetamol 650 mg morning and night for 3 days, and the cough syrup at all three times for 5 days.

## Challenges

A new API key could not use Gemini 2.5 Flash, and a busier model returned a high-demand error. I switched to Gemini 3.5 Flash Lite and added a retry when the service is busy. Photo reading also misreads handwriting, for example mg as wg. The page shows that reading so it can be checked, and the prompt may repair only those obvious mistakes. It may not invent a medicine or a duration.

## Conclusion

Pasted text and the sample slips become a timetable with the dose and the time of day. A photo should still be checked, because handwriting can be misread. A later improvement is to confirm each row before download.
