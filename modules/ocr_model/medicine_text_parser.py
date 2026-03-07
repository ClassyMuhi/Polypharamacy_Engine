"""
medicine_text_parser.py
=======================
Validation and normalisation layer for medicine data extracted by the
Gemini Vision API (or any other OCR source).

Responsibilities
----------------
1. Validate the structure returned by the API.
2. Normalise drug names (lowercase, OCR-typo corrections).
3. Fill in missing metadata fields with sensible defaults.
4. Provide a ``get_medicine_names()`` shortcut for the interaction engine.

Usage
-----
    from modules.ocr_model import MedicineTextParser

    parser = MedicineTextParser()
    cleaned = parser.validate_and_normalise(raw_api_result)
    names   = parser.get_medicine_names(raw_api_result)
"""

from __future__ import annotations

import logging
import re
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# ── Common OCR misread corrections (expandable) ──────────────────────
_OCR_CORRECTIONS: Dict[str, str] = {
    "amoxycillin": "amoxicillin",
    "amoxycillan": "amoxicillin",
    "paracetarnol": "paracetamol",
    "paracetamoi": "paracetamol",
    "patacetamol": "paracetamol",
    "metforrnin": "metformin",
    "metfoumin": "metformin",
    "cetirzine": "cetirizine",
    "cetirizne": "cetirizine",
    "azithromycln": "azithromycin",
    "ibuprofem": "ibuprofen",
    "ibuprufen": "ibuprofen",
    "amlodipne": "amlodipine",
    "losartam": "losartan",
    "atenoloi": "atenolol",
}

# Required keys in each medicine entry
_MEDICINE_KEYS = {"drug_name", "dosage", "frequency", "duration", "route", "instructions"}


class MedicineTextParser:
    """
    Validates and normalises the structured output from the OCR module
    before it is consumed by downstream modules.
    """

    def __init__(self, extra_corrections: Optional[Dict[str, str]] = None):
        """
        Parameters
        ----------
        extra_corrections : dict, optional
            Additional ``{wrong: correct}`` pairs to extend the built-in
            OCR correction table.
        """
        self.corrections = {**_OCR_CORRECTIONS, **(extra_corrections or {})}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def validate_and_normalise(self, ocr_result: Dict) -> Dict:
        """
        Take the raw dict from ``PrescriptionOCR.extract()`` and return
        a cleaned version with normalised drug names and consistent structure.

        Parameters
        ----------
        ocr_result : dict
            Output from ``PrescriptionOCR.extract()``.

        Returns
        -------
        dict
            Same structure but with normalised ``medicines`` list.
        """
        medicines = ocr_result.get("medicines", [])
        cleaned: List[Dict] = []

        for med in medicines:
            entry = self._normalise_entry(med)
            if entry:
                cleaned.append(entry)

        result = {**ocr_result, "medicines": cleaned}
        logger.info(
            "Validated %d → %d medicines (dropped %d invalid).",
            len(medicines),
            len(cleaned),
            len(medicines) - len(cleaned),
        )
        return result

    def get_medicine_names(self, ocr_result: Dict) -> List[str]:
        """
        Convenience method — returns only the normalised drug names.

        This is the primary output consumed by the interaction engine.
        """
        cleaned = self.validate_and_normalise(ocr_result)
        return [m["drug_name"] for m in cleaned["medicines"] if m["drug_name"]]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _normalise_entry(self, entry: Dict) -> Optional[Dict]:
        """Normalise a single medicine entry. Returns None if invalid."""
        if not isinstance(entry, dict):
            return None

        drug_name = entry.get("drug_name")
        if not drug_name or not isinstance(drug_name, str):
            return None

        # Normalise drug name
        drug_name = self.normalize_drug_name(drug_name)
        if not drug_name:
            return None

        # Build clean entry with all expected keys
        return {
            "drug_name": drug_name,
            "dosage": entry.get("dosage") or None,
            "frequency": entry.get("frequency") or None,
            "duration": entry.get("duration") or None,
            "route": entry.get("route") or None,
            "instructions": entry.get("instructions") or None,
        }

    def normalize_drug_name(self, name: str) -> str:
        """
        Clean and normalise a drug name.

        - Lowercase and strip whitespace/punctuation.
        - Apply OCR-misread corrections.
        """
        name = name.lower().strip()
        name = re.sub(r"[^a-z0-9\s\-]", "", name)  # keep alphanumeric, spaces, hyphens
        name = name.strip()

        # Apply corrections
        name = self.corrections.get(name, name)

        return name
