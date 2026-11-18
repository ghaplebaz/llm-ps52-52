"""Save six full screenshots of the running prescription reader."""

from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "screenshots"
WANTED = [
    "01_antibiotic_course",
    "02_acid_and_weekly",
    "04_missing_duration",
    "05_messy_writing",
    "12_inhaler",
    "33_only_if_needed",
]


def labels() -> dict[str, str]:
    found = {}
    for index, path in enumerate(sorted((ROOT / "samples").glob("*.txt"))):
        title = path.stem.split("_", 1)[-1].replace("_", " ")
        found[path.stem] = f"{index + 1:02d} · {title}"
    return found


def choose_sample(page, label: str, needle: str) -> None:
    page.keyboard.press("Escape")
    page.get_by_role("combobox", name="Sample prescriptions (50)").click()
    page.keyboard.type(label)
    option = page.get_by_role("option", name=label, exact=True)
    option.wait_for(timeout=8000)
    option.click()
    page.wait_for_function(
        """(needle) => {
            const box = document.querySelector('textarea');
            return Boolean(box && box.value.includes(needle));
        }""",
        arg=needle,
        timeout=8000,
    )


def shoot(page, slug: str, needle: str) -> None:
    page.get_by_role("heading", name="Morning").wait_for(timeout=90000)
    page.get_by_text(needle, exact=False).first.wait_for(timeout=15000)
    page.wait_for_timeout(500)
    height = page.evaluate(
        """() => document.querySelector('[data-testid="stMainBlockContainer"]').scrollHeight"""
    )
    page.set_viewport_size({"width": 1440, "height": int(height) + 140})
    page.wait_for_timeout(400)
    dest = OUT / f"{slug}.png"
    page.locator('[data-testid="stMainBlockContainer"]').screenshot(path=str(dest))
    print(f"OK {dest.name} {dest.stat().st_size}", flush=True)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    by_slug = labels()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            viewport={"width": 1440, "height": 1100},
            color_scheme="light",
        )
        page.goto("http://localhost:8501", wait_until="domcontentloaded")
        page.get_by_role("button", name="Build schedule").wait_for(timeout=30000)
        for slug in WANTED:
            text = (ROOT / "samples" / f"{slug}.txt").read_text(encoding="utf-8")
            needle = next(line.strip() for line in text.splitlines() if line.strip().startswith(("1.", "Tab", "Cap", "Syp", "Rx")) and len(line.strip()) > 8)
            if needle.startswith("Rx"):
                needle = next(line.strip() for line in text.splitlines() if line.strip()[:2] in {"1.", "2."})
            needle = needle[:28]
            print(f"SHOT {by_slug[slug]} | {needle}", flush=True)
            choose_sample(page, by_slug[slug], needle[:18])
            page.get_by_role("button", name="Build schedule").click()
            try:
                shoot(page, slug, needle[:18])
            except Exception as error:
                page.screenshot(path=str(OUT / f"{slug}-error.png"), full_page=True)
                print(f"FAIL {slug}: {error}", flush=True)
            page.set_viewport_size({"width": 1440, "height": 1100})
        browser.close()


if __name__ == "__main__":
    main()
