import json
import itertools
import os

def load_database(db_path='interactions.json'):
    """Load the drug interactions JSON database."""
    if not os.path.exists(db_path):
        return {"interactions": []}
        
    with open(db_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def check_interactions(medications, db_path='interactions.json'):
    """
    Check for interactions between a list of medications.
    
    Args:
        medications (list): A list of medication names (strings).
        db_path (str): Path to the interactions JSON database.
        
    Returns:
        list: A list of formatted interaction warning strings.
    """
    db = load_database(db_path)
    interactions = db.get('interactions', [])
    
    # Normalize drug names for case-insensitive comparison
    meds_lower = [med.lower() for med in medications]
    warnings = []
    
    # Check every unique pair of medications in the input list
    for (idx1, med1), (idx2, med2) in itertools.combinations(enumerate(meds_lower), 2):
        for record in interactions:
            d1 = record['drug1'].lower()
            d2 = record['drug2'].lower()
            
            # Match pair regardless of order
            if (med1 == d1 and med2 == d2) or (med1 == d2 and med2 == d1):
                # Retrieve the original capitalized names for the output
                orig_med1 = medications[idx1]
                orig_med2 = medications[idx2]
                
                # Format: "High Risk: Warfarin + Aspirin → bleeding risk"
                warning = f"{record['risk']}: {orig_med1} + {orig_med2} → {record['description']}"
                warnings.append(warning)
                
    return warnings

if __name__ == "__main__":
    # Ensure it resolves the relative path correctly if run directly
    db_file = os.path.join(os.path.dirname(__file__), 'interactions.json')
    
    # Test example from requirements
    example_input = ["Warfarin", "Aspirin", "Ibuprofen"]
    print(f"Checking interactions for: {example_input}\n")
    
    results = check_interactions(example_input, db_path=db_file)
    
    if not results:
        print("No interactions found.")
    else:
        for warning in results:
            print(warning)
