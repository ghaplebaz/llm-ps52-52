"""Read text from a prescription photo.

Handwriting is enlarged before it is read. The text is shown in an editor
so a misread dose can be corrected before the schedule is built.
"""

from __future__ import annotations

from pathlib import Path


class OcrUnavailable(Exception):
    pass


def _tesseract_cmd() -> str:
    local = Path(__file__).resolve().parent / ".tesseract" / "bin" / "tesseract"
    if local.exists():
        return str(local)
    return "tesseract"


def read_image(image) -> str:
    try:
        import pytesseract
        from PIL import Image, ImageOps
    except ImportError as error:
        raise OcrUnavailable(
            "Install the OCR libraries with: pip install pytesseract pillow"
        ) from error
    pytesseract.pytesseract.tesseract_cmd = _tesseract_cmd()
    try:
        if not isinstance(image, Image.Image):
            image = Image.open(image)
        gray = ImageOps.grayscale(image)
        gray = gray.resize((gray.width * 2, gray.height * 2), Image.Resampling.LANCZOS)
        text = pytesseract.image_to_string(gray)
    except pytesseract.TesseractNotFoundError as error:
        raise OcrUnavailable(
            "Tesseract is not installed. On macOS run: brew install tesseract. "
            "You can still paste the prescription text."
        ) from error
    except Exception as error:
        raise OcrUnavailable(f"Could not read that image. {error}") from error
    return text.strip()
