"""
OCR Model Module
================
Handles prescription image ingestion via Google Gemini Vision API
and medicine-name normalisation for the polypharmacy analysis pipeline.
"""

from .medicine_text_parser import MedicineTextParser

# PrescriptionOCR is lazily imported so the module can load even when
# google-generativeai is not installed (useful for tests on the parser).
def __getattr__(name):
    if name == "PrescriptionOCR":
        from .prescription_ocr import PrescriptionOCR
        return PrescriptionOCR
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ["PrescriptionOCR", "MedicineTextParser"]
