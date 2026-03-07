import json
import os

class DiseaseConflictChecker:
    def __init__(self, data_path=None):
        if not data_path:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            data_path = os.path.join(base_dir, 'data', 'disease_conflicts.json')
            
        try:
            with open(data_path, 'r') as f:
                self.conflicts_db = json.load(f)
        except Exception as e:
            self.conflicts_db = {}
            print(f"Warning: Could not load disease_conflicts.json from {data_path}. Error: {e}")
            
    def check_conflicts(self, prescriptions, patient_diseases):
        """
        Checks prescriptions against existing patient diseases for contraindications.
        Returns a conflict score (0-100), severity level, and detailed warning list.
        """
        warnings = []
        conflict_score = 0
        
        # Normalize patient diseases for matching
        normalized_diseases = [d.lower() for d in patient_diseases]
        
        import re
        for drug_string in prescriptions:
            match = re.match(r'^([a-zA-Z\s\-]+?)(?:\s+)?(?:\d+(?:\.\d+)?)\s*(?:mg|g|mcg)?$', drug_string.strip(), re.IGNORECASE)
            clean_drug = match.group(1).strip() if match else drug_string.strip()
            
            drug_title = clean_drug.title()
            if drug_title in self.conflicts_db:
                drug_conflicts = self.conflicts_db[drug_title]
                for conflict in drug_conflicts:
                    if conflict["disease"].lower() in normalized_diseases:
                        # Conflict found
                        warnings.append({
                            "drug": drug_title,
                            "disease": conflict["disease"],
                            "severity": conflict["severity"],
                            "reason": conflict["reason"]
                        })
                        
                        # Add to score based on severity (max 100)
                        if conflict["severity"] == "Severe":
                            conflict_score += 60
                        elif conflict["severity"] == "High":
                            conflict_score += 40
                        elif conflict["severity"] == "Moderate":
                            conflict_score += 20
                        else:
                            conflict_score += 10
                            
        total_score = min(100, conflict_score)
        
        if total_score == 0:
            severity = "None"
        elif total_score < 40:
            severity = "Low"
        elif total_score < 70:
            severity = "High"
        else:
            severity = "Severe"
            
        return {
            "score": total_score,
            "severity_level": severity,
            "conflicts": warnings
        }

if __name__ == "__main__":
    checker = DiseaseConflictChecker()
    print("Test 1: Metformin with purely healthy patient")
    print(json.dumps(checker.check_conflicts(["Metformin"], []), indent=2))
    
    print("\nTest 2: Ibuprofen with Chronic Kidney Disease")
    print(json.dumps(checker.check_conflicts(["Ibuprofen", "Lisinopril"], ["Chronic Kidney Disease"]), indent=2))
