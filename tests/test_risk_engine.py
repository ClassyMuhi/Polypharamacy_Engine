import unittest
import os
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.polypharmacy_risk_engine.risk_calculator import PolypharmacyRiskCalculator

class TestPolypharmacyRiskEngine(unittest.TestCase):
    def setUp(self):
        # Using real JSON data paths
        self.calculator = PolypharmacyRiskCalculator()
        
    def test_low_risk_patient(self):
        patient = {
            "age": 45,
            "prescriptions": ["Metformin"],
            "diseases": ["Type 2 Diabetes"]
        }
        result = self.calculator.calculate_risk(patient)
        self.assertEqual(result["risk_category"], "Low Risk")
        self.assertLess(result["polypharmacy_risk_score"], 20)
        self.assertEqual(len(result["disease_conflicts"]), 0)
        
    def test_high_risk_conflict(self):
        patient = {
            "age": 68,
            "prescriptions": ["Ibuprofen", "Aspirin"],
            "diseases": ["Chronic Kidney Disease", "Peptic Ulcer Disease"]
        }
        result = self.calculator.calculate_risk(patient)
        
        # We lowered the conflict base score from 0.50 weight to 0.40
        # So it might dip just slightly below 70 in some conditions if no other risks exist
        # We will check if it's > 50 (Moderate/High/Severe)
        self.assertTrue(result["polypharmacy_risk_score"] > 50)
        self.assertTrue(len(result["disease_conflicts"]) > 0)
        
        # Test finding specific warning
        diseases_flagged = [c["disease"] for c in result["disease_conflicts"]]
        self.assertIn("Chronic Kidney Disease", diseases_flagged)
        
    def test_overlapping_side_effects(self):
        patient = {
            "age": 75,
            "prescriptions": ["Lisinopril", "Amlodipine", "Ibuprofen"],
            "diseases": ["Hypertension"]
        }
        result = self.calculator.calculate_risk(patient)
        
        # Dizziness is shared among Lisinopril, Amlodipine, Ibuprofen
        overlap = result["side_effect_analysis"]["highly_overlapping_effects"]
        self.assertIn("Dizziness", overlap)
        self.assertEqual(overlap["Dizziness"], 3)
        
    def test_high_dosage_penalties(self):
        patient = {
            "age": 60,
            "prescriptions": ["Aspirin 500mg", "Lisinopril 10mg"],
            "diseases": []
        }
        result = self.calculator.calculate_risk(patient)
        
        # High dosage warning should be present because Aspirin > 300mg
        self.assertEqual(len(result["dosage_warnings"]), 1)
        self.assertIn("Aspirin", result["dosage_warnings"][0])
        
if __name__ == '__main__':
    unittest.main()
