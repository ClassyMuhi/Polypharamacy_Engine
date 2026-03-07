import re
from .severity_scoring import SeverityScorer
from .disease_conflict_checker import DiseaseConflictChecker

# Define threshold for high dosages where risks multiply
HIGH_DOSE_THRESHOLDS = {
    "Aspirin": 300,        # >300mg is high dose
    "Ibuprofen": 800,      # >800mg is high dose
    "Metformin": 2000,     # >2000mg is high dose
    "Lisinopril": 40,      # >40mg is high dose
    "Amlodipine": 10       # >10mg is high dose
}

class PolypharmacyRiskCalculator:
    def __init__(self, data_path=None):
        self.severity_scorer = SeverityScorer(data_path)
        self.disease_checker = DiseaseConflictChecker(data_path)
        
    def _parse_dosage(self, drug_string):
        """
        Extracts base drug name and numeric dosage from a string.
        e.g., "Aspirin 500mg" -> ("Aspirin", 500.0)
        "Metformin" -> ("Metformin", None)
        """
        # Match word characters (drug name) potentially followed by spaces and a number connected to mg/g
        match = re.match(r'^([a-zA-Z\s\-]+?)(?:\s+)?(\d+(?:\.\d+)?)\s*(?:mg|g|mcg)?$', drug_string.strip(), re.IGNORECASE)
        
        if match:
            drug_name = match.group(1).strip().title()
            try:
                dosage = float(match.group(2))
                return drug_name, dosage
            except ValueError:
                return drug_name, None
        
        # If no dosage found, just return the cleaned string
        return drug_string.strip().title(), None
        
    def calculate_risk(self, patient_profile):
        """
        Calculates the overall polypharmacy risk score.
        patient_profile should be a dict containing:
        {
            "age": int,
            "prescriptions": list of strings,
            "diseases": list of strings
        }
        """
        age = patient_profile.get("age", 0)
        prescriptions = patient_profile.get("prescriptions", [])
        diseases = patient_profile.get("diseases", [])
        
        num_drugs = len(prescriptions)
        
        # 1. Base Score calculation (Number of drugs and Patient Age)
        # Polypharmacy typically defined as taking >= 5 medications
        drug_count_score = min(40, (num_drugs ** 1.3) * 2) # Exponential growth for more drugs
        
        # Age risk: Starts slightly at 60, rises significantly above 65
        age_score = 0
        if age >= 65:
            age_score = min(20, (age - 60) * 1.5)
            
        base_risk = drug_count_score + age_score
        
        # 2. Side Effect Burden Score
        side_effect_assessment = self.severity_scorer.analyze_prescriptions(prescriptions)
        side_effect_score = side_effect_assessment["score"]
        
        # 3. Disease Conflicts Score
        conflict_assessment = self.disease_checker.check_conflicts(prescriptions, diseases)
        conflict_score = conflict_assessment["score"]
        
        # 4. High Dosage Penalties
        dosage_penalty = 0
        high_dose_warnings = []
        
        for raw_drug in prescriptions:
            base_name, dosage = self._parse_dosage(raw_drug)
            if dosage and base_name in HIGH_DOSE_THRESHOLDS:
                if dosage > HIGH_DOSE_THRESHOLDS[base_name]:
                    dosage_penalty += 15 # Severe penalty for exceeding recommended high dosage
                    high_dose_warnings.append(
                        f"{base_name} dose of {dosage}mg exceeds recommended high-dose threshold of {HIGH_DOSE_THRESHOLDS[base_name]}mg."
                    )
        
        # 5. Final Weighted Score Calculation (0-100)
        # We weigh the conflicts heavily, followed by side effects, then base parameters and dosage.
        final_score = (base_risk * 0.20) + (side_effect_score * 0.30) + (conflict_score * 0.40) + dosage_penalty
        final_score = min(100.0, max(0.0, round(final_score, 2)))
        
        # Determine Final Categorization
        if final_score < 20:
            category = "Low Risk"
        elif final_score < 50:
            category = "Moderate Risk"
        elif final_score < 75:
            category = "High Risk"
        else:
            category = "Severe Risk"
            
        return {
            "patient_age": age,
            "num_medications": num_drugs,
            "polypharmacy_risk_score": final_score,
            "risk_category": category,
            "side_effect_analysis": {
                "severity_level": side_effect_assessment["severity_level"],
                "highly_overlapping_effects": side_effect_assessment["overlapping_side_effects"]
            },
            "dosage_warnings": high_dose_warnings,
            "disease_conflicts": conflict_assessment["conflicts"],
            "recommendation": self._generate_recommendation(category)
        }
        
    def _generate_recommendation(self, category):
        if category == "Low Risk":
            return "Standard monitoring. Continue current plan."
        elif category == "Moderate Risk":
            return "Review medication list for potential simplifications. Monitor for side effects."
        elif category == "High Risk":
            return "Comprehensive medication review strongly advised. Consider alternative therapies for conflicting drugs."
        else:
            return "URGENT intervention required. High probability of adverse drug events. Deprescribe explicitly conflicting medications immediately."

if __name__ == "__main__":
    import json
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description='Polypharmacy Risk Engine - Calculate risk for a patient profile.')
    parser.add_argument('--age', type=int, default=72, help='Age of the patient (e.g., 72)')
    parser.add_argument('--drugs', nargs='+', default=["Aspirin", "Ibuprofen", "Lisinopril", "Metformin", "Amlodipine"],
                        help='List of prescribed medications (e.g., --drugs Aspirin Lisinopril Metformin)')
    parser.add_argument('--diseases', nargs='*', default=["Hypertension", "Type 2 Diabetes", "Peptic Ulcer Disease"],
                        help='List of existing conditions (e.g., --diseases Hypertension "Type 2 Diabetes")')
                        
    args = parser.parse_args()
    
    calculator = PolypharmacyRiskCalculator()
    
    sample_patient = {
        "age": args.age,
        "prescriptions": args.drugs,
        "diseases": args.diseases
    }
    
    print("--- Perfect Output for Polypharmacy Risk Engine ---")
    print(f"Analyzing patient: {args.age} yrs old")
    print(f"Drugs: {', '.join(args.drugs)}")
    print(f"Diseases: {', '.join(args.diseases) if args.diseases else 'None'}\n")
    print(json.dumps(calculator.calculate_risk(sample_patient), indent=2))
