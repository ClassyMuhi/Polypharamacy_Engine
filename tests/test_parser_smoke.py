"""
Smoke-test for MedicineTextParser — verifies regex extraction logic
without needing EasyOCR or any images.
"""
import sys, os

# Ensure the project root is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Import directly to avoid the easyocr dependency pulled in by __init__.py
from modules.ocr_model.medicine_text_parser import MedicineTextParser

SAMPLE_OCR_TEXT = """
Dr. Smith  |  City Hospital  |  Date: 2026-03-07
Patient: John Doe  Age: 45

Rx:
1. Amoxicillin 500mg  1-0-1  x 5 days  oral  after food
2. Paracetamol 650mg  1-1-1  x 3 days
3. Pantoprazole 40mg  once daily  before food
4. Cetirizine 10mg  0-0-1  x 7 days
5. Metformin 500mg  BD  oral  after meals
"""

parser = MedicineTextParser()
results = parser.parse(SAMPLE_OCR_TEXT)

print("=" * 60)
print(f"  Parsed {len(results)} medicine entries")
print("=" * 60)

for i, med in enumerate(results, 1):
    print(f"\n--- Medicine #{i} ---")
    for k, v in med.items():
        if v:
            print(f"  {k:15s}: {v}")

names = parser.get_medicine_names(SAMPLE_OCR_TEXT)
print("\n" + "=" * 60)
print("  Drug names for interaction engine:", names)
print("=" * 60)
