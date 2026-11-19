"""Build the two-page A4 procedure report."""

from pathlib import Path

from fpdf import FPDF
from PIL import Image

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
SCREENSHOT = PROJECT / "screenshots" / "01_antibiotic_course.png"
PDF_PATH = ROOT / "Report.pdf"
INPUT_CROP = ROOT / "input-sample.png"
OUTPUT_CROP = ROOT / "output-sample.png"

INK = (32, 40, 36)
GREEN = (27, 74, 56)
RULE = (214, 220, 216)
PAPER = (246, 248, 246)
PROMPT = (252, 250, 245)


def crops() -> None:
    image = Image.open(SCREENSHOT)
    width, _height = image.size
    image.crop((0, 268, width, 800)).save(INPUT_CROP)
    image.crop((0, 828, width, 1410)).save(OUTPUT_CROP)


class Report(FPDF):
    def header(self) -> None:
        if self.page_no() == 1:
            self.set_fill_color(*GREEN)
            self.rect(0, 0, 210, 26, "F")
            self.set_text_color(255, 255, 255)
            self.set_xy(16, 6)
            self.set_font("Helvetica", "B", 16)
            self.cell(0, 8, "Prescription Reader")
            self.set_xy(16, 15)
            self.set_font("Helvetica", "", 11)
            self.cell(0, 6, "Problem statement 52    Procedure report")
            self.set_text_color(*INK)
            self.set_y(32)
        else:
            self.set_fill_color(*GREEN)
            self.rect(0, 0, 210, 9, "F")
            self.set_text_color(255, 255, 255)
            self.set_xy(16, 2.2)
            self.set_font("Helvetica", "", 10)
            self.cell(120, 5, "Prescription Reader")
            self.cell(58, 5, "Rushikesh Wankhede  |  Roll 52", align="R")
            self.set_text_color(*INK)
            self.set_y(14)

    def footer(self) -> None:
        self.set_y(-12)
        self.set_draw_color(*GREEN)
        self.set_line_width(0.35)
        self.line(16, self.get_y(), 194, self.get_y())
        self.ln(1.4)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(90, 98, 94)
        self.cell(self.epw * 0.72, 4.5, "Rushikesh Wankhede   |   Class LYAIA7   |   Roll 52")
        self.cell(self.epw * 0.28, 4.5, f"{self.page_no()} of {{nb}}", align="R")
        self.set_text_color(*INK)

    def section(self, title: str) -> None:
        self.ln(2.4)
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(*GREEN)
        self.cell(self.epw, 5.5, title)
        self.ln(6)
        y = self.get_y()
        self.set_draw_color(*GREEN)
        self.set_line_width(0.45)
        self.line(self.l_margin, y, self.l_margin + 22, y)
        self.set_draw_color(*RULE)
        self.set_line_width(0.2)
        self.line(self.l_margin + 22, y, self.l_margin + self.epw, y)
        self.ln(2)
        self.set_text_color(*INK)

    def paragraph(self, text: str) -> None:
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "", 12)
        self.set_text_color(*INK)
        self.multi_cell(self.epw, 5.3, text)

    def meta_table(self) -> None:
        rows = [
            ("Project title", "Prescription Reader", "PS number", "52"),
            ("Name", "Rushikesh Wankhede", "Roll number", "52"),
            ("Class", "LYAIA7", "Model", "Gemini 3.5 Flash Lite"),
        ]
        label_w, value_w = 34, 60
        row_h = 7.4
        x0, y0 = self.l_margin, self.get_y()
        self.set_draw_color(*RULE)
        self.set_line_width(0.2)
        for index, (left_label, left_value, right_label, right_value) in enumerate(rows):
            y = y0 + index * row_h
            fill = (238, 243, 239) if index % 2 == 0 else (255, 255, 255)
            self.set_fill_color(*fill)
            self.rect(x0, y, self.epw, row_h, "FD")
            self.set_xy(x0 + 2, y + 1.2)
            self.set_font("Helvetica", "B", 12)
            self.cell(label_w, 5, left_label)
            self.set_font("Helvetica", "", 12)
            self.cell(value_w, 5, left_value)
            self.set_font("Helvetica", "B", 12)
            self.cell(30, 5, right_label)
            self.set_font("Helvetica", "", 12)
            self.cell(46, 5, right_value)
        y = y0 + 3 * row_h
        self.set_fill_color(255, 255, 255)
        self.rect(x0, y, self.epw, row_h, "FD")
        self.set_xy(x0 + 2, y + 1.2)
        self.set_font("Helvetica", "B", 12)
        self.cell(label_w, 5, "GitHub link")
        self.set_font("Helvetica", "", 12)
        self.cell(self.epw - label_w - 4, 5, "https://github.com/ghaplebaz/prescription-reader")
        self.set_y(y + row_h + 1)

    def prompt_box(self, text: str) -> None:
        self.set_font("Helvetica", "", 12)
        inner_w = self.epw - 8
        lines = self.multi_cell(inner_w, 5.1, text, dry_run=True, output="LINES")
        height = len(lines) * 5.1 + 5
        x, y = self.l_margin, self.get_y() + 1
        self.set_fill_color(*PROMPT)
        self.set_draw_color(214, 206, 190)
        self.rect(x, y, self.epw, height, "FD")
        self.set_fill_color(*GREEN)
        self.rect(x, y, 1.4, height, "F")
        self.set_xy(x + 4, y + 2.4)
        self.set_text_color(*INK)
        self.multi_cell(inner_w, 5.1, text)
        self.set_y(y + height + 1)

    def figure(self, path: Path, caption: str, width: float) -> None:
        self.ln(1.2)
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "I", 12)
        self.set_text_color(70, 78, 74)
        self.multi_cell(self.epw, 5.2, caption)
        self.ln(0.8)
        with Image.open(path) as image:
            height = width * image.height / image.width
        x = self.l_margin + (self.epw - width) / 2
        y = self.get_y()
        self.set_draw_color(206, 212, 208)
        self.set_line_width(0.25)
        self.rect(x - 0.4, y - 0.4, width + 0.8, height + 0.8)
        self.image(str(path), x=x, y=y, w=width, h=height)
        self.set_y(y + height + 1.2)
        self.set_text_color(*INK)


def build() -> None:
    crops()
    pdf = Report(format="A4")
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.set_margins(16, 14, 16)
    pdf.add_page()
    pdf.meta_table()

    pdf.section("Problem statement")
    pdf.paragraph(
        "Handwritten prescriptions use codes such as 1-0-1, BD and HS, so the time of day is easy to mix up. "
        "This project turns the slip into a timetable of medicine, dose, morning, afternoon, night and days. "
        "It helps a patient follow a prescription they already have, and it is not medical advice."
    )

    pdf.section("Tools and model")
    pdf.paragraph(
        "I used Python and Streamlit for the page. Photo reading uses Pillow and pytesseract. "
        "The model is Gemini 3.5 Flash Lite through the Gemini API (gemini-3.5-flash-lite). "
        "The key stays in a local .env file and is not uploaded. I did not train a model. "
        "Gemini 2.5 Flash was not available on a new key, so this is the model that answered."
    )

    pdf.section("Procedure")
    steps = [
        "1. I matched roll number 52 to problem statement 52, Prescription Reader.",
        "2. I created a Gemini API key and saved it only in .env.",
        "3. My first prompt asked for a free-text schedule. The columns changed between runs, and a missing duration was sometimes filled in.",
        "4. I rewrote the prompt so the answer is one JSON object, and days stay empty when the slip does not state a duration.",
        "5. I built the page and 50 fictional slips. Each slip has typed text and a handwritten-style photo.",
        "6. I tested pasted text and photo reading. Text read from a photo is shown in a box so it can be corrected before the timetable is built.",
    ]
    for step in steps:
        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", "", 12)
        pdf.multi_cell(pdf.epw, 5.2, step)

    pdf.section("Prompt used")
    pdf.paragraph(
        "The first prompt asked for free text, so the model renamed columns and sometimes invented a duration. "
        "The final prompt asks for JSON and forbids a guessed number of days."
    )
    pdf.prompt_box(
        "You convert prescription text into a medication timetable. You only copy what is written. "
        "You do not add a medicine, a dose, or a duration. Return only JSON with patient_name, doctor_name, "
        "date, medicines and unclear. Each medicine has medicine, dose, morning, afternoon, night, days, "
        "instruction and frequency_raw. A code such as 1-0-1 is morning, afternoon and night. OD is morning, "
        "BD is morning and night, TDS is all three, and HS is night only. SOS is not placed on the daily clock; "
        'the instruction is "only if needed". If no duration is written, days is null. Do not guess a number.'
    )

    pdf.add_page()
    pdf.section("Results")
    pdf.paragraph(
        "Sample 01 is an antibiotic course. The input is the typed slip beside the handwritten photo. "
        "The output places Amoxicillin 500 mg morning, afternoon and night for 5 days, Paracetamol 650 mg morning and night for 3 days, "
        "and the cough syrup at all three times for 5 days."
    )
    pdf.figure(INPUT_CROP, "Figure 1. Sample input: typed slip and the handwritten photo.", 148)
    pdf.figure(OUTPUT_CROP, "Figure 2. Sample output: morning, afternoon, night, and the full table.", 148)

    pdf.section("Challenges")
    pdf.paragraph(
        "A new API key could not use Gemini 2.5 Flash, and a busier model returned a high-demand error. "
        "I switched to Gemini 3.5 Flash Lite and added a retry when the service is busy. "
        "Photo reading also misreads handwriting, for example mg as wg. The page shows that reading so it can be checked, "
        "and the prompt may repair only those obvious mistakes. It may not invent a medicine or a duration."
    )

    pdf.section("Conclusion")
    pdf.paragraph(
        "Pasted text and the sample slips become a timetable with the dose and the time of day. "
        "A photo should still be checked, because handwriting can be misread. "
        "A later improvement is to confirm each row before download."
    )
    pdf.output(PDF_PATH)
    print(f"pages={pdf.pages_count} file={PDF_PATH}")


if __name__ == "__main__":
    build()
