"""
main.py
-------
Entry point for the Medicine Interaction and Polypharmacy Risk Checker
for Elderly Patients.

Demonstrates the system using two sample patients:
  1. Mr. Raj Kumar  – 72 years old, 6 medications (polypharmacy + interactions)
  2. Mrs. Priya Nair – 65 years old, 3 safe medications (no interactions)
"""

from patient import Patient
from interaction_engine import InteractionEngine


def main():
    engine = InteractionEngine()

    # ──────────────────────────────────────────────────────────────────────
    # Demo Patient 1: High-risk elderly patient on many medications
    # ──────────────────────────────────────────────────────────────────────
    print("\n" + "=" * 50)
    print("  CASE 1: Mr. Raj Kumar (High-Risk Patient)")
    print("=" * 50)

    patient1 = Patient(name="Raj Kumar", age=72)
    patient1.add_medication("Aspirin")
    patient1.add_medication("Warfarin")
    patient1.add_medication("Ibuprofen")
    patient1.add_medication("Metformin")
    patient1.add_medication("Atorvastatin")
    patient1.add_medication("Amoxicillin")   # 6 medications → polypharmacy risk

    engine.check_interactions(patient1)

    # ──────────────────────────────────────────────────────────────────────
    # Demo Patient 2: Low-risk patient on simple medications
    # ──────────────────────────────────────────────────────────────────────
    print("\n" + "=" * 50)
    print("  CASE 2: Mrs. Priya Nair (Low-Risk Patient)")
    print("=" * 50)

    patient2 = Patient(name="Priya Nair", age=65)
    patient2.add_medication("Paracetamol")
    patient2.add_medication("Metformin")
    patient2.add_medication("Atorvastatin")  # 3 medications, mild or no clashes

    engine.check_interactions(patient2)


if __name__ == "__main__":
    main()
