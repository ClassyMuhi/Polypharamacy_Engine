"""
patient.py
----------
Defines the Patient class for the Medicine Interaction and
Polypharmacy Risk Checker for Elderly Patients.
"""


class Patient:
    """
    Represents a patient and stores their personal details
    and current list of medications.
    """

    def __init__(self, name: str, age: int):
        """
        Initialize a Patient.

        Args:
            name (str): Full name of the patient.
            age  (int): Age of the patient in years.
        """
        self.name = name
        self.age = age
        self.medications: list[str] = []   # List of medication names

    def add_medication(self, medication: str) -> None:
        """
        Add a medication to the patient's medication list.

        Args:
            medication (str): Name of the medication (case-insensitive storage).
        """
        med = medication.strip()
        if med:
            self.medications.append(med)

    def print_profile(self) -> None:
        """Print a formatted summary of the patient's profile."""
        print("===========================================")
        print("  Patient Profile")
        print("===========================================")
        print(f"  Name : {self.name}")
        print(f"  Age  : {self.age} years")
        print(f"  Medications ({len(self.medications)}):")
        for med in self.medications:
            print(f"    - {med}")
        print("===========================================")
