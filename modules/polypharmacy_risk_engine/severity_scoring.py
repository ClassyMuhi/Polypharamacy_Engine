import json
import os
from collections import Counter

class SeverityScorer:
    def __init__(self, data_path=None):
        if not data_path:
            # Default path assuming it's run from project root, but allow override
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            data_path = os.path.join(base_dir, 'data', 'side_effects.json')
            
        try:
            with open(data_path, 'r') as f:
                self.side_effects_db = json.load(f)
        except Exception as e:
            # Fallback for testing or missing file
            self.side_effects_db = {}
            print(f"Warning: Could not load side_effects.json from {data_path}. Error: {e}")
            
    def analyze_prescriptions(self, prescriptions):
        """
        Analyzes a list of prescribed drugs and calculates a cumulative side-effect burden.
        Returns a score (0-100), severity level, and the list of highly overlapping side effects.
        """
        all_side_effects = []
        import re
        for drug_string in prescriptions:
            # Strip potential dosages like " 500mg" before matching
            match = re.match(r'^([a-zA-Z\s\-]+?)(?:\s+)?(?:\d+(?:\.\d+)?)\s*(?:mg|g|mcg)?$', drug_string.strip(), re.IGNORECASE)
            clean_drug = match.group(1).strip() if match else drug_string.strip()
            
            # Assume case-insensitivity for matching
            drug_title = clean_drug.title()
            if drug_title in self.side_effects_db:
                all_side_effects.extend(self.side_effects_db[drug_title])
                
        # Count occurrences of each side effect
        effect_counts = Counter(all_side_effects)
        
        # Identify overlapping side effects (occurring more than once)
        overlapping_effects = {effect: count for effect, count in effect_counts.items() if count > 1}
        
        # Calculate burden score
        # Base formula: 5 points per unique side effect + 15 points per overlap instance
        base_score = len(effect_counts) * 5
        overlap_score = sum((count - 1) * 15 for count in overlapping_effects.values())
        
        total_score = min(100, base_score + overlap_score)
        
        # Determine severity level
        if total_score < 20:
            severity = "Low"
        elif total_score < 50:
            severity = "Moderate"
        elif total_score < 80:
            severity = "High"
        else:
            severity = "Severe"
            
        return {
            "score": total_score,
            "severity_level": severity,
            "overlapping_side_effects": overlapping_effects,
            "all_reported_effects": dict(effect_counts)
        }

if __name__ == "__main__":
    # Test execution
    scorer = SeverityScorer()
    print("Test 1: Metformin + Lisinopril")
    print(json.dumps(scorer.analyze_prescriptions(["Metformin", "Lisinopril"]), indent=2))
    
    print("\nTest 2: Amlodipine + Lisinopril + Ibuprofen (Dizziness overlap)")
    print(json.dumps(scorer.analyze_prescriptions(["Amlodipine", "Lisinopril", "Ibuprofen"]), indent=2))
