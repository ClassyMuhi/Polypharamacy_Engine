"""
prescription_ocr.py
===================
Extracts medicine information from prescription images using the
**Google Gemini Vision API**.

The image is sent directly to the model with a structured prompt.
Gemini handles both OCR *and* entity extraction in a single call,
returning a JSON list of medicines with dosage, frequency, etc.

Usage
-----
    from modules.ocr_model import PrescriptionOCR

    ocr = PrescriptionOCR()
    result = ocr.extract("path/to/prescription.jpg")
    # result => { "medicines": [...], "raw_text": "..." }
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional

import google.genai as genai
from PIL import Image

# Lazy import — only needed for PDFs
try:
    from pdf2image import convert_from_path
except ImportError:
    convert_from_path = None

logger = logging.getLogger(__name__)

# ── Prompt sent alongside the image ──────────────────────────────────
_EXTRACTION_PROMPT = """You are a medical prescription reader. Analyse this prescription image
and extract ALL medicines listed.

Return ONLY valid JSON (no markdown fences, no explanation) in this exact format:
{
  "patient_name": "name or null",
  "patient_age": age_number_or_null,
  "date": "date string or null",
  "raw_text": "all text you can see on the prescription",
  "medicines": [
    {
      "drug_name": "lowercase generic drug name",
      "dosage": "e.g. 500mg",
      "frequency": "e.g. 1-0-1 or twice daily",
      "duration": "e.g. 5 days",
      "route": "e.g. oral",
      "instructions": "e.g. after food"
    }
  ]
}

Rules:
- Use the GENERIC drug name in lowercase (e.g. "paracetamol" not "Dolo-650").
- If a field is unclear or missing, set it to null.
- Do NOT invent medicines that aren't on the prescription.
- Extract EVERY medicine, even if partially readable.
"""


class PrescriptionOCR:
    """Extracts structured prescription data via Google Gemini Vision."""

    _IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}
    _PDF_EXTENSIONS = {".pdf"}

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        """
        Parameters
        ----------
        api_key : str, optional
            Gemini API key.  Falls back to ``config.GEMINI_API_KEY``.
        model_name : str, optional
            Gemini model to use.  Falls back to ``config.GEMINI_MODEL``.
        """
        # Import config here so the module can still be imported without .env
        from config import GEMINI_API_KEY, GEMINI_MODEL

        self.api_key = api_key or GEMINI_API_KEY
        self.model_name = model_name or GEMINI_MODEL

        if not self.api_key:
            raise ValueError(
                "Gemini API key not found. "
                "Set GEMINI_API_KEY in your .env file or pass it directly."
            )

        self.client = genai.Client(api_key=self.api_key)
        logger.info("Gemini Vision initialised (model=%s)", self.model_name)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def extract(self, file_path: str) -> Dict:
        """
        Extract structured prescription data from an image or PDF.

        Parameters
        ----------
        file_path : str
            Path to a prescription image (.jpg, .png, etc.) or PDF.

        Returns
        -------
        dict
            Standard data-contract dict with keys:
            ``patient_name``, ``patient_age``, ``date``,
            ``raw_text``, ``medicines``.
        """
        images = self._load_file(file_path)
        all_medicines: List[Dict] = []
        raw_texts: List[str] = []
        result: Dict = {}

        for idx, img in enumerate(images):
            logger.info("Processing page %d of %d …", idx + 1, len(images))
            page_result = self._call_gemini(img)
            all_medicines.extend(page_result.get("medicines", []))
            raw_texts.append(page_result.get("raw_text", ""))
            # Keep patient info from first page
            if idx == 0:
                result = page_result

        result["medicines"] = all_medicines
        result["raw_text"] = "\n".join(raw_texts)

        logger.info(
            "Extraction complete — %d medicines from '%s'",
            len(all_medicines),
            file_path,
        )
        return result

    def extract_medicine_names(self, file_path: str) -> List[str]:
        """Convenience: returns just the drug names (for the interaction engine)."""
        result = self.extract(file_path)
        return [
            m["drug_name"]
            for m in result.get("medicines", [])
            if m.get("drug_name")
        ]

    # ------------------------------------------------------------------
    # Gemini API call
    # ------------------------------------------------------------------

    def _call_gemini(self, image: Image.Image) -> Dict:
        """Send image + prompt to Gemini and parse the JSON response."""
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[_EXTRACTION_PROMPT, image],
                config=genai.types.GenerateContentConfig(
                    temperature=0.1,  # low creativity for accuracy
                ),
            )
            text = response.text.strip()
            logger.debug("Gemini raw response: %s", text[:200])
            return self._parse_response(text)

        except Exception as e:
            logger.error("Gemini API error: %s", e)
            return {"medicines": [], "raw_text": f"[API ERROR] {e}"}

    @staticmethod
    def _parse_response(text: str) -> Dict:
        """Parse Gemini's response text into a dict, handling markdown fences."""
        # Strip markdown code fences if present
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            logger.warning("Could not parse Gemini response as JSON, returning raw text.")
            data = {"medicines": [], "raw_text": text}

        # Normalise drug names to lowercase
        for med in data.get("medicines", []):
            if med.get("drug_name"):
                med["drug_name"] = med["drug_name"].lower().strip()

        return data

    # ------------------------------------------------------------------
    # File loading
    # ------------------------------------------------------------------

    def _load_file(self, file_path: str) -> List[Image.Image]:
        """Load image or PDF and return a list of PIL Images."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Prescription file not found: {file_path}")

        ext = path.suffix.lower()

        if ext in self._IMAGE_EXTENSIONS:
            return [Image.open(path).convert("RGB")]
        elif ext in self._PDF_EXTENSIONS:
            return self._load_pdf(str(path))
        else:
            raise ValueError(
                f"Unsupported file type '{ext}'.  "
                f"Supported: {self._IMAGE_EXTENSIONS | self._PDF_EXTENSIONS}"
            )

    @staticmethod
    def _load_pdf(file_path: str) -> List[Image.Image]:
        """Convert PDF pages to PIL Images."""
        if convert_from_path is None:
            raise ImportError(
                "pdf2image is required for PDF support. "
                "Install: pip install pdf2image"
            )
        return convert_from_path(file_path, dpi=300)
