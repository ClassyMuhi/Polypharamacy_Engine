"""
test_real_image.py
==================
Scans the `test_images/` folder and runs the Gemini Vision OCR pipeline
on every prescription image/PDF found.

Usage
-----
    # from medsafe-polypharmacy-checker/ :
    python tests/test_real_image.py                         # all images in test_images/
    python tests/test_real_image.py test_images/rx4.png     # specific file
"""

import sys
import os
from pathlib import Path

# Project root on sys.path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from modules.ocr_model.prescription_ocr import PrescriptionOCR
from modules.ocr_model.medicine_text_parser import MedicineTextParser

SUPPORTED = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp", ".pdf"}
TEST_IMAGES_DIR = ROOT / "test_images"


def process_file(file_path: Path, ocr: PrescriptionOCR, parser: MedicineTextParser):
    print("\n" + "=" * 60)
    print(f"  FILE: {file_path.name}")
    print("=" * 60)

    # --- Step 1: Gemini Vision extraction ---
    print("  Calling Gemini Vision API...")
    raw_result = ocr.extract(str(file_path))

    # Show raw text the model saw
    raw_text = raw_result.get("raw_text", "")
    print("\n  RAW TEXT FROM PRESCRIPTION:")
    print("  " + "\n  ".join(raw_text.splitlines()) if raw_text.strip() else "  (none)")

    # --- Step 2: Validate & normalise ---
    cleaned = parser.validate_and_normalise(raw_result)
    medicines = cleaned.get("medicines", [])

    print(f"\n  EXTRACTED MEDICINES ({len(medicines)} found):")
    if medicines:
        for i, med in enumerate(medicines, 1):
            print(f"\n    [{i}] {med['drug_name'].upper()}")
            if med["dosage"]:        print(f"         Dosage      : {med['dosage']}")
            if med["frequency"]:     print(f"         Frequency   : {med['frequency']}")
            if med["duration"]:      print(f"         Duration    : {med['duration']}")
            if med["route"]:         print(f"         Route       : {med['route']}")
            if med["instructions"]:  print(f"         Instructions: {med['instructions']}")
    else:
        print("    No medicines extracted.")

    # --- Output for interaction engine ---
    names = parser.get_medicine_names(raw_result)
    print(f"\n  -> OUTPUT FOR INTERACTION ENGINE: {names}")


def main():
    if len(sys.argv) >= 2:
        targets = [Path(sys.argv[1])]
        if not targets[0].exists():
            print(f"[ERROR] File not found: {targets[0]}")
            sys.exit(1)
    else:
        if not TEST_IMAGES_DIR.exists():
            print(f"[ERROR] test_images/ folder not found at: {TEST_IMAGES_DIR}")
            sys.exit(1)
        targets = sorted(
            f for f in TEST_IMAGES_DIR.iterdir()
            if f.is_file() and f.suffix.lower() in SUPPORTED
        )
        if not targets:
            print(f"No images found in {TEST_IMAGES_DIR}/")
            print("  Drop your prescription images (.jpg/.png/.pdf) and re-run.")
            sys.exit(0)

    print(f"\nFound {len(targets)} file(s) to process.")
    print("Initialising Gemini Vision...")

    ocr = PrescriptionOCR()
    parser = MedicineTextParser()

    for path in targets:
        process_file(path, ocr, parser)

    print("\n" + "=" * 60)
    print("  Done.")
    print("=" * 60)


if __name__ == "__main__":
    main()
