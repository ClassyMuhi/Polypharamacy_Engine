"""
interaction_engine.py
---------------------
Defines the InteractionEngine class, which checks a patient's medication
list for dangerous drug-drug interactions and polypharmacy risks.

Also defines the in-memory drug interaction database used for lookups.
"""

import sys
import os

# ── Load environment variables from .env via project config ──────────────
# Walk up from this file's location to find config.py at the repo root
_repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

try:
    import config  # loads .env and exposes GEMINI_API_KEY, GEMINI_MODEL
    _GEMINI_API_KEY = config.GEMINI_API_KEY
    _GEMINI_MODEL   = config.GEMINI_MODEL
except ImportError:
    _GEMINI_API_KEY = ""
    _GEMINI_MODEL   = "gemini-2.5-flash"

from itertools import combinations
from typing import Optional
from drug import Drug, Severity
from patient import Patient


# ---------------------------------------------------------------------------
# In-Memory Drug Interaction Database
# ---------------------------------------------------------------------------
# Each entry is a Drug object describing ONE directional/bidirectional pair.
# The matches() method handles both orderings automatically.

DRUG_DATABASE: list[Drug] = [
    # ── HIGH severity interactions ──────────────────────────────────────────
    Drug("Aspirin",      "Warfarin",       Severity.HIGH,     "Serious bleeding risk: both inhibit clotting"),
    Drug("Warfarin",     "Ibuprofen",      Severity.HIGH,     "Ibuprofen displaces Warfarin, raising bleeding risk"),
    Drug("Metformin",    "Ibuprofen",      Severity.HIGH,     "NSAIDs reduce kidney function, increasing Metformin toxicity"),

    # ── MODERATE severity interactions ──────────────────────────────────────
    Drug("Aspirin",      "Ibuprofen",      Severity.MODERATE, "Both NSAIDs - increased GI bleeding and ulcer risk"),
    Drug("Warfarin",     "Amoxicillin",    Severity.MODERATE, "Amoxicillin alters gut flora and potentiates Warfarin"),
    Drug("Atorvastatin", "Amoxicillin",    Severity.MODERATE, "Minor increase in statin plasma levels"),
    Drug("Aspirin",      "Metformin",      Severity.MODERATE, "High-dose Aspirin may mask hypoglycemia symptoms"),

    # ── LOW severity interactions ────────────────────────────────────────────
    Drug("Paracetamol",  "Warfarin",       Severity.LOW,      "Long-term high-dose Paracetamol can mildly enhance anticoagulation"),
    Drug("Atorvastatin", "Paracetamol",    Severity.LOW,      "Rarely clinically significant; monitor liver enzymes"),
    Drug("Amoxicillin",  "Metformin",      Severity.LOW,      "Possible minor effect; usually well tolerated"),
]


# ---------------------------------------------------------------------------
# Polypharmacy threshold (clinical guideline: ≥ 5 medications)
# ---------------------------------------------------------------------------
POLYPHARMACY_THRESHOLD = 5


class InteractionEngine:
    """
    Analyses a patient's medication list for:
      1. Drug-drug interactions (checked against DRUG_DATABASE)
      2. Polypharmacy risk (≥ 5 medications)
    """

    def __init__(self, database: Optional[list[Drug]] = None):
        """
        Initialise the engine with an optional custom database.
        Defaults to the built-in DRUG_DATABASE.

        Args:
            database (list[Drug]): List of Drug interaction entries.
        """
        self.database = database if database is not None else DRUG_DATABASE

    # ------------------------------------------------------------------
    def check_interactions(self, patient: Patient) -> None:
        """
        Run the full interaction check for the given patient and
        print a formatted report to stdout.

        Steps:
          1. Print patient profile header.
          2. Check every unordered pair of medications against the database.
          3. Warn about polypharmacy if applicable.

        Args:
            patient (Patient): The patient whose medications to check.
        """
        patient.print_profile()
        print("\n--- Drug Interaction Report ---\n")

        medications = patient.medications

        # ── Step 1: Pairwise interaction check ──────────────────────────
        interactions_found = False

        # combinations() generates every unique (med_a, med_b) pair once
        for med_a, med_b in combinations(medications, 2):
            interaction = self._find_interaction(med_a, med_b)
            if interaction:
                interactions_found = True
                self._print_interaction_alert(interaction, med_a, med_b)

        if not interactions_found:
            print("  [OK] No drug interactions detected.\n")

        # ── Step 2: Polypharmacy risk check ─────────────────────────────
        self._check_polypharmacy(patient)

        print("\n--- End of Report ---\n")

    # ------------------------------------------------------------------
    def _find_interaction(self, drug_a: str, drug_b: str) -> Drug | None:
        """
        Search the database for an interaction between two drugs.

        Args:
            drug_a (str): First drug name.
            drug_b (str): Second drug name.

        Returns:
            Drug | None: The matching Drug entry, or None if not found.
        """
        for entry in self.database:
            if entry.matches(drug_a, drug_b):
                return entry
        return None

    # ------------------------------------------------------------------
    @staticmethod
    def _print_interaction_alert(interaction: Drug, med_a: str, med_b: str) -> None:
        """
        Print a formatted alert for a single drug-drug interaction.

        Args:
            interaction (Drug): The matched database entry.
            med_a       (str):  First medication name (as entered by patient).
            med_b       (str):  Second medication name.
        """
        severity = interaction.severity.value
        description = interaction.description

        # Choose a plain-text label by severity level (ASCII-safe for all terminals)
        label = {"HIGH": "[!!HIGH!!]", "MODERATE": "[!MODERATE]", "LOW": "[LOW]"}.get(severity, "[ALERT]")

        print(f"  {label} Interaction Detected:")
        print(f"       {med_a} + {med_b}")
        print(f"       Severity    : {severity}")
        print(f"       Description : {description}")
        print()

    # ------------------------------------------------------------------
    @staticmethod
    def _check_polypharmacy(patient: Patient) -> None:
        """
        Check whether the patient's medication count meets or exceeds
        the polypharmacy threshold and print a warning if so.

        Args:
            patient (Patient): The patient to evaluate.
        """
        count = len(patient.medications)
        if count >= POLYPHARMACY_THRESHOLD:
            print(
                f"  [WARNING] Polypharmacy Risk Detected: {patient.name} is taking "
                f"{count} medications (>= {POLYPHARMACY_THRESHOLD}).\n"
                "          Please consult a clinical pharmacist for a medication review."
            )
        else:
            print(
                f"  [OK] No polypharmacy risk detected "
                f"({count} of {POLYPHARMACY_THRESHOLD} threshold)."
            )
