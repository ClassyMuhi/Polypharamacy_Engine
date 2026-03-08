import os
import sys
import json
from itertools import combinations

root_dir = os.path.abspath(os.path.dirname(__file__))

def clear_modules_cache():
    for key in list(sys.modules.keys()):
        if key == "modules" or key.startswith("modules.") or key == "config":
            del sys.modules[key]

# 1. Setup Root Imports
sys.path.insert(0, root_dir)
from modules.ocr_model.prescription_ocr import PrescriptionOCR
from modules.ocr_model.medicine_text_parser import MedicineTextParser
from modules.polypharmacy_risk_engine.risk_calculator import PolypharmacyRiskCalculator
import config
sys.path.remove(root_dir)
clear_modules_cache()

# 2. Setup HC-03 Imports
hc03_dir = os.path.join(root_dir, "hc03_system")
sys.path.insert(0, hc03_dir)
from modules.report_generator import ReportGenerator
sys.path.remove(hc03_dir)
clear_modules_cache()

# 3. Setup MedicineInteractionChecker Imports
med_dir = os.path.join(root_dir, "MedicineInteractionChecker")
sys.path.insert(0, med_dir)
from patient import Patient
from interaction_engine import InteractionEngine

# Restore root path for standard operation
sys.path.insert(0, root_dir)

def main():
    print("==================================================")
    print("      MEDSAFE POLYPHARMACY FULL PIPELINE TEST     ")
    print("==================================================")

    image_path = "test_images/rx3.png"
    if not os.path.exists(image_path):
        print(f"Error: Could not find {image_path}. Please provide a valid image.")
        return

    # 1. OCR Stage
    print(f"\n[1] Running OCR on {image_path}...")
    try:
        ocr = PrescriptionOCR()
        raw_result = ocr.extract(image_path)
    except Exception as e:
        print(f"OCR failed. Have you set GEMINI_API_KEY in .env? Error: {e}")
        return

    # 2. Parsing Stage
    print("\n[2] Parsing and normalizing medicine names...")
    parser = MedicineTextParser()
    clean_result = parser.validate_and_normalise(raw_result)
    medicine_names = parser.get_medicine_names(raw_result)
    
    # Capitalize for consistency
    medicine_names = [m.title() for m in medicine_names]
    print(f"    Extracted: {', '.join(medicine_names) if medicine_names else 'None'}")
    
    if not medicine_names:
        print("    No medicines found in the prescription. Using fallback test data.")
        medicine_names = ["Aspirin", "Warfarin", "Ibuprofen", "Metformin", "Amoxicillin"]

    # 3. Interaction Engine
    print("\n[3] Checking for Drug Interactions...")
    patient = Patient("Test Patient", age=72)
    for m in medicine_names:
        patient.add_medication(m)

    engine = InteractionEngine()
    interactions = []
    
    # Calculate combinations and look up in database
    for med_a, med_b in combinations(medicine_names, 2):
        interaction = engine._find_interaction(med_a, med_b)
        if interaction:
            interactions.append({
                "drug_1": med_a,
                "drug_2": med_b,
                "severity": interaction.severity.name.capitalize(), # e.g. "High"
                "clinical_risk": interaction.description
            })
            
    print(f"    Found {len(interactions)} pairwise interactions.")

    # 4. Polypharmacy Risk Engine
    print("\n[4] Calculating Polypharmacy Risk Score...")
    risk_calc = PolypharmacyRiskCalculator()
    patient_profile = {
        "age": patient.age,
        "prescriptions": medicine_names,
        "diseases": ["Hypertension", "Type 2 Diabetes"] # Adding sample diseases to test
    }
    risk_result = risk_calc.calculate_risk(patient_profile)
    print(f"    Risk Score: {risk_result['polypharmacy_risk_score']}/100 ({risk_result['risk_category']})")

    # 5. Report Generation (HC-03 System)
    print("\n[5] Generating final clinical report...")
    report_gen = ReportGenerator()
    
    patient_data = {
        "patient_id": "P_PIPELINE_TEST",
        "age": patient.age,
        "medications": medicine_names,
        "interactions": interactions,
    }

    # Generate Text Report
    report = report_gen.generate_report(patient_data, output_format="text")
    
    if "error" in report:
        print(f"\nReport Generation Failed: {report['error']}")
    else:
        print("\n\n" + report.get("formatted_report", "No report generated."))
        
        # Also generate PDF to test PDF export functionality
        pdf_report = report_gen.generate_report(patient_data, output_format="pdf")
        if pdf_report.get("status") == "success":
            print(f"\n    PDF Report cleanly generated: {pdf_report.get('pdf_path')}")

if __name__ == "__main__":
    main()
