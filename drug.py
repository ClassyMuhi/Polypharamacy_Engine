"""
drug.py
-------
Defines the Drug class and Severity enum for the Medicine Interaction
and Polypharmacy Risk Checker for Elderly Patients.
"""

from enum import Enum


class Severity(Enum):
    """Severity levels for drug-drug interactions."""
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"


class Drug:
    """
    Represents a single drug-drug interaction entry in the database.

    Each entry captures:
    - Which two drugs interact
    - How severe the interaction is (LOW / MODERATE / HIGH)
    - A short clinical description of the effect
    """

    def __init__(
        self,
        name: str,
        interacts_with: str,
        severity: Severity,
        description: str,
    ):
        """
        Initialize a Drug interaction entry.

        Args:
            name          (str):      Primary drug name.
            interacts_with(str):      Name of the drug it interacts with.
            severity      (Severity): Severity of the interaction.
            description   (str):      Clinical description of the interaction.
        """
        self.name = name
        self.interacts_with = interacts_with
        self.severity = severity
        self.description = description

    def matches(self, drug_a: str, drug_b: str) -> bool:
        """
        Check whether this entry describes an interaction between the two
        given drug names (order-independent, case-insensitive).

        Args:
            drug_a (str): First drug name.
            drug_b (str): Second drug name.

        Returns:
            bool: True if this entry matches the pair.
        """
        a, b = drug_a.lower(), drug_b.lower()
        return (
            (self.name.lower() == a and self.interacts_with.lower() == b)
            or (self.name.lower() == b and self.interacts_with.lower() == a)
        )
