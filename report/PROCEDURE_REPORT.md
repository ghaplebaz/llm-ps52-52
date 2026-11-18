# Prescription Reader

**Project title:** Prescription Reader
**PS number:** 52
**Name:** ________________
**Roll number:** 52
**Class:** ________________
**GitHub link:** ________________

## Problem statement

Handwritten prescriptions use short codes such as 1-0-1, BD, TDS, OD, and HS. A patient can miss a dose or mix up morning and night. This tool reads that text, including a photo of the slip, and lays out medicine name, dose, time of day, and number of days. It helps a patient follow a slip they already have. It does not decide treatment. The page says this is not medical advice.

## Tools and model

Python and Streamlit. The model is Gemini 3.5 Flash Lite through the Gemini API. The key stays in a local `.env` file and is listed in `.gitignore`. Photo reading uses Pillow and pytesseract. Gemini 2.5 Flash is no longer available on a new key, so the working model name is `gemini-3.5-flash-lite`. No model was trained.

## Procedure

1. I matched roll number 52 to problem 52, Prescription Reader.
2. I created a Gemini API key and stored it only in `.env`.
3. I first asked the model for a free-text schedule. The columns changed between runs, and a missing duration was sometimes filled in.
4. I rewrote the prompt so the answer is one JSON object with medicine, dose, morning, afternoon, night, and days. Days must be null when the slip does not state a duration. The prompt also repairs common handwriting misreads such as wg for mg, without adding a medicine that is not written.
5. I wrote the Python call, the timetable page, and 50 fictional slips. Each slip has a text file and a handwritten-style photo.
6. I tested pasted text and photos. The text from a photo is shown in an editor so it can be corrected before the schedule is built.

## Prompt used

The final prompt is in `prompts.py`. It maps 1-0-1, OD, BD, TDS, and HS onto morning, afternoon, and night, and it forbids a guessed number of days.

The change that improved it: the first prompt asked for free text. The final prompt asks for JSON and leaves days empty when no duration is written.

## Results

Sample 01, a short antibiotic slip, returns Amoxicillin 500 mg morning, afternoon, and night for 5 days, and Paracetamol morning and night for 3 days. Sample 02 keeps a weekly vitamin off the daily clock. Sample 04 leaves Days as “not stated” when the slip has no duration, and lists an “only if needed” medicine separately. Screenshots of these runs are in the `screenshots` folder.

## Challenges

A new API key could not use Gemini 2.5 Flash, and a busier model returned “high demand”, so the app uses Gemini 3.5 Flash Lite and retries a busy call. Handwriting is misread: mg can become wg, and a name can lose a letter. The page shows that reading so it can be corrected. The model is told to repair only those obvious misreads and not to invent a medicine or a duration.

## Conclusion

Pasted text and the 50 sample slips become a timetable with dose and time of day. A photo still depends on the reading of the handwriting, so the text should be checked before download. A later version could ask the user to confirm each row.

Write your name, class, and GitHub link in the header. Export this file as a 2-page A4 PDF in 12-point font and upload it as `Report.pdf`.
