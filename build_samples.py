"""Write 50 fictional prescription slips and matching handwritten photos.

These are demo text for the mini project. They are not real prescriptions.
"""

from __future__ import annotations

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
TEXT_DIR = ROOT / "samples"
PHOTO_DIR = TEXT_DIR / "photos"

SLIPS = [
    ("01_antibiotic_course", "City Clinic, Pune", "Dr. A. Kulkarni", "12 Nov 2026", "R. Deshmukh, 34 yrs", ["Rx", "Tab Amoxicillin 500 mg 1-1-1 x 5 days after food", "Tab Paracetamol 650 mg 1-0-1 x 3 days if fever", "Syrup cough relief 5 ml 1-1-1 x 5 days"]),
    ("02_acid_and_weekly", "Care Clinic", "Dr. N. Shah", "18 Nov 2026", "A. Patel", ["Rx", "Tab Pantoprazole 40 mg OD empty stomach x 14 days", "Cap Vitamin D3 60,000 IU once weekly x 8 weeks", "Tab Cetirizine 10 mg HS x 7 days", "Tab Azithromycin 500 mg OD x 3 days"]),
    ("03_diabetes_visit", "Family Clinic", "Dr. S. Iyer", "04 Nov 2026", "Meera Joshi", ["Rx", "Tab Metformin 500 mg BD x 30 days after food", "Tab Atorvastatin 10 mg HS x 30 days", "Tab Calcium 500 mg OD morning x 30 days", "Syp Lactulose 15 ml HS x 7 days", "Tab Ondansetron 4 mg TDS x 3 days if vomiting"]),
    ("04_missing_duration", "City Hospital", "Dr. R. Menon", "02 Nov 2026", "K. Sharma", ["Rx", "Tab Ibuprofen 400 mg 1-0-1 after food", "Tab Rabeprazole 20 mg OD before breakfast x 10 days", "Eye drops Moxifloxacin 1 drop 1-1-1 right eye", "Tab Alprazolam 0.25 mg SOS for anxiety"]),
    ("05_messy_writing", "Night OPD", "Dr. P. Rao", "09 Nov 2026", "S. Khan", ["Rx", "Tab Amoxicillin 500 mg 1-1-1 x 5 days PC", "Tab Paracetamol 650 mg 1-0-1 x 3 days", "Syp Ambroxol 5 ml BD x 5 days", "Cap Omeprazole 20 mg OD x 14 days AC", "Tab Levocetirizine 5 mg HS x 5 days"]),
    ("06_cold_and_cough", "Lake Clinic", "Dr. V. Kulkarni", "11 Nov 2026", "N. Bhosale", ["Rx", "Tab Levocetirizine 5 mg HS x 5 days", "Tab Paracetamol 500 mg 1-0-1 x 3 days if fever", "Syp Ambroxol 5 ml TDS x 5 days", "Nasal drops saline 2 drops BD x 5 days"]),
    ("07_child_fever", "Child Care", "Dr. M. Desai", "08 Nov 2026", "A. Shaikh, 6 yrs", ["Rx", "Syp Paracetamol 5 ml 1-0-1 x 3 days if fever", "Syp Cetirizine 5 ml HS x 5 days", "ORS one packet after each loose stool x 2 days"]),
    ("08_eye_infection", "Vision Clinic", "Dr. H. Patil", "15 Nov 2026", "L. Jain", ["Rx", "Eye drops Moxifloxacin 1 drop 1-1-1 x 7 days right eye", "Eye drops lubricant 1 drop BD x 7 days", "Tab Cetirizine 10 mg HS x 5 days"]),
    ("09_ear_pain", "ENT Clinic", "Dr. K. Nair", "03 Nov 2026", "P. Shetty", ["Rx", "Ear drops ofloxacin 3 drops TDS x 5 days", "Tab Ibuprofen 400 mg 1-0-1 x 3 days after food", "Tab Cetirizine 10 mg HS x 5 days"]),
    ("10_acidity", "City Clinic", "Dr. A. Kulkarni", "19 Nov 2026", "G. More", ["Rx", "Tab Pantoprazole 40 mg OD empty stomach x 14 days", "Syp Antacid 10 ml TDS x 5 days after food", "Tab Domperidone 10 mg TDS x 5 days before food"]),
    ("11_blood_pressure", "Heart Clinic", "Dr. R. Kulkarni", "01 Nov 2026", "S. Reddy, 58 yrs", ["Rx", "Tab Amlodipine 5 mg OD morning x 30 days", "Tab Telmisartan 40 mg OD morning x 30 days", "Tab Atorvastatin 10 mg HS x 30 days"]),
    ("12_inhaler", "Chest Clinic", "Dr. F. Khan", "06 Nov 2026", "I. Qureshi", ["Rx", "Inhaler Salbutamol 2 puffs SOS if wheeze", "Inhaler Budesonide 2 puffs BD x 30 days", "Tab Montelukast 10 mg HS x 30 days"]),
    ("13_thyroid", "Endocrine Clinic", "Dr. S. Iyer", "10 Nov 2026", "P. Kulkarni", ["Rx", "Tab Thyroxine 50 mcg OD empty stomach x 30 days", "Tab Calcium 500 mg OD lunch x 30 days", "Cap Vitamin D3 60,000 IU once weekly x 8 weeks"]),
    ("14_iron_course", "Women Clinic", "Dr. A. Bose", "14 Nov 2026", "R. Gupta", ["Rx", "Tab Iron folic acid 1 tab OD after lunch x 30 days", "Tab Vitamin C 500 mg OD morning x 30 days", "Syp Iron 5 ml OD x 30 days if tablets not taken"]),
    ("15_fever_support", "Night OPD", "Dr. P. Rao", "16 Nov 2026", "M. Yadav", ["Rx", "Tab Paracetamol 650 mg 1-0-1 x 3 days if fever", "ORS 200 ml after each loose stool x 2 days", "Tab Ondansetron 4 mg TDS x 2 days if vomiting", "Tab Pantoprazole 40 mg OD x 5 days"]),
    ("16_dental_pain", "Dental Care", "Dr. J. Mehta", "07 Nov 2026", "C. Naik", ["Rx", "Tab Ibuprofen 400 mg 1-0-1 x 3 days after food", "Tab Amoxicillin 500 mg 1-1-1 x 5 days", "Tab Pantoprazole 40 mg OD x 5 days before breakfast"]),
    ("17_skin_rash", "Skin Clinic", "Dr. L. Fernandes", "13 Nov 2026", "D. Pinto", ["Rx", "Cream Mometasone apply BD x 7 days on the rash", "Tab Cetirizine 10 mg HS x 7 days", "Tab Pantoprazole 40 mg OD x 7 days"]),
    ("18_urine_infection", "City Hospital", "Dr. R. Menon", "05 Nov 2026", "H. Kaur", ["Rx", "Tab Nitrofurantoin 100 mg BD x 5 days after food", "Tab Paracetamol 500 mg 1-0-1 x 3 days if pain", "ORS one glass TDS x 3 days"]),
    ("19_headache_sos", "Neuro Clinic", "Dr. V. Kulkarni", "17 Nov 2026", "E. D'Souza", ["Rx", "Tab Naproxen 250 mg SOS for headache after food", "Tab Domperidone 10 mg SOS with the pain tablet", "Tab Amitriptyline 10 mg HS x 14 days"]),
    ("20_weekly_vitamin", "Family Clinic", "Dr. N. Shah", "20 Nov 2026", "B. Joshi", ["Rx", "Cap Vitamin D3 60,000 IU once weekly x 8 weeks", "Tab Calcium 500 mg OD x 30 days", "Tab B complex 1 tab OD x 30 days"]),
    ("21_antenatal", "Women Clinic", "Dr. A. Bose", "02 Nov 2026", "S. Pawar", ["Rx", "Tab Folic acid 5 mg OD morning x 30 days", "Tab Iron 1 tab OD after lunch x 30 days", "Tab Calcium 500 mg OD at night x 30 days"]),
    ("22_after_procedure", "Day Care", "Dr. J. Mehta", "11 Nov 2026", "T. Salve", ["Rx", "Tab Ibuprofen 400 mg 1-0-1 after food", "Tab Amoxicillin 500 mg 1-1-1 x 5 days", "Tab Pantoprazole 40 mg OD x 5 days"]),
    ("23_long_antibiotic", "City Hospital", "Dr. H. Patil", "09 Nov 2026", "V. Chavan", ["Rx", "Tab Cefixime 200 mg BD x 7 days", "Tab Pantoprazole 40 mg OD x 7 days", "Tab Paracetamol 650 mg SOS if fever"]),
    ("24_night_allergy", "Lake Clinic", "Dr. F. Khan", "06 Nov 2026", "O. Sheikh", ["Rx", "Tab Cetirizine 10 mg HS x 10 days", "Tab Montelukast 10 mg HS x 10 days", "Nasal spray 2 sprays HS x 10 days"]),
    ("25_sugar_and_bp", "Heart Clinic", "Dr. R. Kulkarni", "12 Nov 2026", "W. Patil, 62 yrs", ["Rx", "Tab Metformin 500 mg BD x 30 days after food", "Tab Glimepiride 1 mg OD before breakfast x 30 days", "Tab Amlodipine 5 mg OD morning x 30 days", "Tab Atorvastatin 20 mg HS x 30 days"]),
    ("26_child_loose_stools", "Child Care", "Dr. M. Desai", "04 Nov 2026", "Y. Khan, 4 yrs", ["Rx", "ORS 100 ml after each loose stool x 3 days", "Syp Zinc 5 ml OD x 14 days", "Syp Paracetamol 5 ml SOS if fever"]),
    ("27_blocked_nose", "ENT Clinic", "Dr. K. Nair", "18 Nov 2026", "Z. Ansari", ["Rx", "Nasal drops xylometazoline 2 drops BD x 3 days", "Tab Levocetirizine 5 mg HS x 5 days", "Steam inhalation BD x 5 days"]),
    ("28_antacid_only", "Care Clinic", "Dr. N. Shah", "15 Nov 2026", "F. Lopes", ["Rx", "Syp Antacid 10 ml TDS x 5 days after meals", "Tab Pantoprazole 40 mg OD x 14 days", "Tab Simethicone SOS if bloating"]),
    ("29_cholesterol_only", "Heart Clinic", "Dr. R. Kulkarni", "03 Nov 2026", "U. Banerjee", ["Rx", "Tab Atorvastatin 20 mg HS x 30 days", "Tab Aspirin 75 mg OD after lunch x 30 days", "Cap Omega 3 1 cap OD x 30 days"]),
    ("30_dry_eyes", "Vision Clinic", "Dr. H. Patil", "19 Nov 2026", "Q. Merchant", ["Rx", "Eye drops lubricant 1 drop 1-0-1 both eyes", "Tab Cetirizine 10 mg HS x 5 days"]),
    ("31_discharge_sheet", "City Hospital", "Dr. R. Menon", "01 Nov 2026", "J. Kamble", ["Rx", "Tab Cefixime 200 mg BD x 5 days", "Tab Pantoprazole 40 mg OD x 5 days", "Tab Paracetamol 650 mg 1-0-1 x 3 days", "Tab Domperidone 10 mg TDS x 3 days", "ORS 200 ml TDS x 3 days", "Tab Vitamin C 500 mg OD x 7 days"]),
    ("32_three_timings", "Family Clinic", "Dr. S. Iyer", "08 Nov 2026", "K. Iyer", ["Rx", "Tab Amoxicillin 500 mg TDS x 5 days", "Tab Pantoprazole 40 mg OD x 5 days", "Tab Cetirizine 10 mg HS x 5 days", "Syp Cough 5 ml BD x 5 days"]),
    ("33_only_if_needed", "Night OPD", "Dr. P. Rao", "14 Nov 2026", "L. Dhumal", ["Rx", "Tab Paracetamol 650 mg SOS if fever", "Tab Ondansetron 4 mg SOS if vomiting", "Tab Ibuprofen 400 mg SOS if pain after food"]),
    ("34_weekly_injection", "Endocrine Clinic", "Dr. S. Iyer", "07 Nov 2026", "N. Kulkarni", ["Rx", "Inj Vitamin B12 1 ml once weekly x 4 weeks", "Tab Folic acid 5 mg OD x 30 days", "Tab Iron 1 tab OD after lunch x 30 days"]),
    ("35_three_day_course", "City Clinic", "Dr. A. Kulkarni", "16 Nov 2026", "P. Gaikwad", ["Rx", "Tab Azithromycin 500 mg OD x 3 days after food", "Tab Paracetamol 650 mg 1-0-1 x 3 days", "Tab Pantoprazole 40 mg OD x 3 days"]),
    ("36_syrup_tds", "Child Care", "Dr. M. Desai", "10 Nov 2026", "R. Jadhav, 8 yrs", ["Rx", "Syp Amoxicillin 5 ml TDS x 5 days", "Syp Paracetamol 5 ml SOS if fever", "Syp Cetirizine 5 ml HS x 5 days"]),
    ("37_ear_and_tablet", "ENT Clinic", "Dr. K. Nair", "12 Nov 2026", "S. Borkar", ["Rx", "Ear drops ciprofloxacin 4 drops TDS x 7 days", "Tab Cefixime 200 mg BD x 5 days", "Tab Ibuprofen 400 mg 1-0-1 x 3 days"]),
    ("38_one_tablet_wording", "Lake Clinic", "Dr. V. Kulkarni", "05 Nov 2026", "A. Shinde", ["Rx", "Tab Cetirizine 1 tab HS x 7 days", "Tab Pantoprazole 1 tab OD x 14 days", "Syp Antacid 2 teaspoons TDS x 5 days"]),
    ("39_both_eyes", "Vision Clinic", "Dr. H. Patil", "11 Nov 2026", "B. Khot", ["Rx", "Eye drops antibiotic 1 drop QID x 5 days both eyes", "Eye drops lubricant 1 drop BD x 7 days", "Tab Cetirizine 10 mg HS x 3 days"]),
    ("40_bedtime_only", "Neuro Clinic", "Dr. V. Kulkarni", "18 Nov 2026", "C. Rane", ["Rx", "Tab Amitriptyline 10 mg HS x 14 days", "Tab Pantoprazole 40 mg OD morning x 14 days", "Tab Paracetamol 500 mg SOS if headache"]),
    ("41_ocr_fever", "Night OPD", "Dr. P. Rao", "09 Nov 2026", "D. Mane", ["Rx", "T@b Paracetam0l 650 mg 1-0-1 x 3 days", "Tab Azithr0mycin 500 mg OD x 3 days", "Syp C0ugh 5 ml BD x 5 days"]),
    ("42_ocr_sugar", "Family Clinic", "Dr. S. Iyer", "13 Nov 2026", "E. Kale", ["Rx", "Tab Metf0rmin 500 mg BD x 30 days", "Tab Glimepiride 1 mg OD x 30 days", "Tab Atorvastain 10 mg HS x 30 days"]),
    ("43_ocr_pain", "Dental Care", "Dr. J. Mehta", "06 Nov 2026", "F. Sawant", ["Rx", "Tab Ibufen 400 mg 1-0-1 x 3 days PC", "Tab Am0xicillin 500 mg 1-1-1 x 5 days", "Cap Omepraz0le 20 mg OD x 5 days AC"]),
    ("44_ocr_skin", "Skin Clinic", "Dr. L. Fernandes", "17 Nov 2026", "G. Naidu", ["Rx", "Cream apply BD x 7 days", "Tab Cetirizne 10 mg HS x 7 days", "Tab Pant0prazole 40 mg OD x 7 days"]),
    ("45_ocr_child", "Child Care", "Dr. M. Desai", "04 Nov 2026", "H. Pathan, 5 yrs", ["Rx", "Syp Paracetam0l 5 ml SOS fever", "ORS after each loose stool x 2 days", "Syp Zinc 5 ml OD x 14 days"]),
    ("46_senior_list", "Heart Clinic", "Dr. R. Kulkarni", "02 Nov 2026", "I. Deshpande, 70 yrs", ["Rx", "Tab Amlodipine 5 mg OD x 30 days", "Tab Metformin 500 mg BD x 30 days", "Tab Atorvastatin 10 mg HS x 30 days", "Tab Aspirin 75 mg OD after food x 30 days", "Tab Pantoprazole 40 mg OD x 30 days", "Cap Vitamin D3 60,000 IU once weekly x 8 weeks"]),
    ("47_sprain", "Sports Clinic", "Dr. J. Mehta", "15 Nov 2026", "J. Thorat", ["Rx", "Tab Ibuprofen 400 mg 1-0-1 x 5 days after food", "Tab Pantoprazole 40 mg OD x 5 days", "Gel Diclofenac apply BD x 5 days", "Tab Paracetamol 650 mg SOS if pain remains"]),
    ("48_food_upset", "Night OPD", "Dr. P. Rao", "19 Nov 2026", "K. Mhatre", ["Rx", "Tab Ofloxacin 200 mg BD x 5 days", "Tab Ornidazole 500 mg BD x 5 days", "Tab Racecadotril 100 mg TDS x 3 days", "ORS 200 ml after each loose stool x 3 days", "Tab Pantoprazole 40 mg OD x 5 days"]),
    ("49_sinus", "ENT Clinic", "Dr. K. Nair", "08 Nov 2026", "M. Ghorpade", ["Rx", "Tab Levocetirizine 5 mg HS x 7 days", "Tab Montelukast 10 mg HS x 7 days", "Nasal spray 2 sprays BD x 7 days", "Steam inhalation BD x 7 days", "Tab Paracetamol 500 mg SOS if headache"]),
    ("50_follow_up", "City Clinic, Pune", "Dr. A. Kulkarni", "20 Nov 2026", "N. Wagh", ["Rx", "Tab Cefpodoxime 200 mg BD x 5 days", "Tab Pantoprazole 40 mg OD x 5 days empty stomach", "Tab Paracetamol 650 mg 1-0-1 x 3 days", "Syp Cough 10 ml TDS x 5 days", "Tab Cetirizine 10 mg HS x 5 days", "Cap Multivitamin 1 cap OD x 15 days"]),
]


def write_texts() -> None:
    TEXT_DIR.mkdir(exist_ok=True)
    for old in TEXT_DIR.glob("*.txt"):
        old.unlink()
    for slug, clinic, doctor, date, patient, lines in SLIPS:
        body = "\n".join([clinic, doctor, f"Date: {date}", f"Patient: {patient}", "", *lines])
        (TEXT_DIR / f"{slug}.txt").write_text(body + "\n", encoding="utf-8")


def write_photos() -> None:
    PHOTO_DIR.mkdir(exist_ok=True)
    for old in PHOTO_DIR.glob("*.png"):
        old.unlink()
    hand = ImageFont.truetype("/System/Library/Fonts/Supplemental/Bradley Hand Bold.ttf", 42)
    label = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 22)
    label_bold = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 28)
    random.seed(52)
    for slug, clinic, doctor, date, patient, lines in SLIPS:
        width = 1200
        row_h = 64
        height = 230 + row_h * (len(lines) + 1) + 160
        paper = Image.new("RGB", (width, height), "#f4efe4")
        draw = ImageDraw.Draw(paper)
        for y in range(200, height - 90, row_h):
            draw.line((70, y + 36, width - 70, y + 36), fill="#e4d7c4", width=2)
        draw.rectangle((36, 36, width - 36, height - 36), outline="#8d7b62", width=3)
        draw.text((70, 52), clinic, font=label_bold, fill="#3d3428")
        draw.text((70, 90), f"{doctor}    {date}", font=label, fill="#5c5144")
        draw.text((70, 132), f"Patient: {patient}", font=hand, fill="#1a2744")
        draw.line((70, 186, width - 90, 190), fill="#1a2744", width=2)
        y = 210
        for line in lines:
            draw.text((78 + random.randint(-3, 5), y), line, font=hand, fill="#1a2744")
            y += row_h
        draw.text((width - 360, height - 130), doctor.split()[-1], font=hand, fill="#1a2744")
        draw.text((70, height - 68), "Demo sample. Not a real prescription.", font=label, fill="#8a7b68")
        tilted = paper.rotate(random.uniform(-1.1, 1.1), resample=Image.Resampling.BICUBIC, expand=True, fillcolor="#d9d3c7")
        tilted = tilted.filter(ImageFilter.SMOOTH)
        tilted.save(PHOTO_DIR / f"{slug}.png", "PNG")


if __name__ == "__main__":
    write_texts()
    write_photos()
    print(f"{len(SLIPS)} slips")
    print(f"{len(list(TEXT_DIR.glob('*.txt')))} texts")
    print(f"{len(list(PHOTO_DIR.glob('*.png')))} photos")
