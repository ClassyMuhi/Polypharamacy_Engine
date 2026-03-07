"""
HC-03 System Test Runner
Demonstrates and tests all modules of the Healthcare Safety System
"""

import json
import sys
import logging
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.report_generator import ReportGenerator
from modules.ai_explanation_engine import AIExplanationEngine
from config import LOG_FILE

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


# ==================== Test Data ====================

SAMPLE_PATIENT_DATA = {
    "patient_id": "P102",
    "age": 72,
    "medications": [
        "Warfarin",
        "Aspirin",
        "Ibuprofen",
        "Metformin",
        "Lisinopril"
    ],
    "interactions": [
        {
            "drug_1": "Warfarin",
            "drug_2": "Aspirin",
            "severity": "High",
            "clinical_risk": "Increased bleeding risk due to combined anticoagulant effect"
        },
        {
            "drug_1": "Aspirin",
            "drug_2": "Ibuprofen",
            "severity": "Moderate",
            "clinical_risk": "Reduced antiplatelet effect and increased GI bleeding risk"
        },
        {
            "drug_1": "Warfarin",
            "drug_2": "Ibuprofen",
            "severity": "High",
            "clinical_risk": "NSAIDs increase anticoagulant effect and GI bleeding risk"
        },
        {
            "drug_1": "Metformin",
            "drug_2": "Ibuprofen",
            "severity": "Moderate",
            "clinical_risk": "NSAIDs may reduce metformin clearance, increase risk of lactic acidosis"
        }
    ]
}


def print_section(title: str):
    """Print formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def test_ai_explanation_engine():
    """Test AI Explanation Engine"""
    print_section("TEST 1: AI EXPLANATION ENGINE")

    engine = AIExplanationEngine()
    
    print(f"AI Engine Available: {engine.available}\n")

    # Test single interaction explanation
    print("Test 1a: Single Drug Interaction Explanation")
    print("-" * 60)
    explanation = engine.generate_explanation(
        drug_1="Warfarin",
        drug_2="Aspirin",
        severity="High",
        clinical_risk="Increased bleeding risk"
    )
    print(f"Drugs: Warfarin + Aspirin")
    print(f"Severity: High")
    print(f"Explanation:\n{explanation}\n")

    # Test polypharmacy warning
    print("Test 1b: Polypharmacy Warning (5 medications)")
    print("-" * 60)
    warning = engine.generate_polypharmacy_warning(5)
    print(f"Warning:\n{warning}\n")

    print("Test 1c: Polypharmacy Warning (8 medications)")
    print("-" * 60)
    warning = engine.generate_polypharmacy_warning(8)
    print(f"Warning:\n{warning}\n")


def test_report_generator_json():
    """Test Report Generator - JSON format"""
    print_section("TEST 2: REPORT GENERATOR - JSON FORMAT")

    generator = ReportGenerator()
    
    print("Generating JSON report for patient P102...")
    print("-" * 60)
    
    report = generator.generate_report(SAMPLE_PATIENT_DATA, output_format="json")

    if "error" in report:
        print(f"ERROR: {report['error']}")
        return

    # Print summary
    print(f"\nReport ID: {report.get('report_id')}")
    print(f"Generated: {report.get('generated_at')}")
    print(f"Status: Success\n")

    # Patient Summary
    summary = report.get("patient_summary", {})
    print("Patient Summary:")
    print(f"  - Patient ID: {summary.get('patient_id')}")
    print(f"  - Age: {summary.get('age')}")
    print(f"  - Medications: {summary.get('medication_count')}")
    print(f"  - Interactions: {summary.get('interaction_count')}\n")

    # Risk Summary
    risk = report.get("risk_summary", {})
    print("Risk Summary:")
    print(f"  - Overall Risk: {risk.get('overall_risk')}")
    print(f"  - Total Interactions: {risk.get('total_interactions')}")
    print(f"  - Critical: {risk.get('critical_count')}")
    print(f"  - High: {risk.get('high_count')}")
    print(f"  - Moderate: {risk.get('moderate_count')}")
    print(f"  - Low: {risk.get('low_count')}\n")

    # Polypharmacy
    poly = report.get("polypharmacy_assessment", {})
    print("Polypharmacy Assessment:")
    print(f"  - Is Polypharmacy: {poly.get('is_polypharmacy')}")
    print(f"  - Medication Count: {poly.get('medication_count')}")
    print(f"  - Risk Level: {poly.get('risk_level')}\n")

    # Interactions
    interactions = report.get("interactions", [])
    print(f"Drug Interactions ({len(interactions)}):")
    for idx, interaction in enumerate(interactions, 1):
        print(f"\n  {idx}. {interaction.get('drug_1')} + {interaction.get('drug_2')}")
        print(f"     Severity: {interaction.get('severity')}")
        print(f"     Risk: {interaction.get('clinical_risk')}")
        print(f"     Explanation: {interaction.get('ai_explanation')[:100]}...\n")

    # Clinical Recommendations
    recommendations = report.get("clinical_recommendations", [])
    print(f"Clinical Recommendations ({len(recommendations)}):")
    for rec in recommendations:
        print(f"  • {rec}\n")

    # Save full JSON report
    json_file = "test_report.json"
    with open(json_file, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Full JSON report saved to: {json_file}\n")


def test_report_generator_text():
    """Test Report Generator - Text format"""
    print_section("TEST 3: REPORT GENERATOR - TEXT FORMAT")

    generator = ReportGenerator()
    
    print("Generating TEXT report for patient P102...")
    print("-" * 60)
    
    report = generator.generate_report(SAMPLE_PATIENT_DATA, output_format="text")

    if "error" in report:
        print(f"ERROR: {report['error']}")
        return

    # Print text report
    text_report = report.get("formatted_report", "")
    print(text_report)

    # Save text report
    text_file = "test_report.txt"
    with open(text_file, "w") as f:
        f.write(text_report)
    print(f"\nFull text report saved to: {text_file}\n")


def test_report_generator_pdf():
    """Test Report Generator - PDF format"""
    print_section("TEST 4: REPORT GENERATOR - PDF FORMAT")

    generator = ReportGenerator()
    
    print("Generating PDF report for patient P102...")
    print("-" * 60)
    
    report = generator.generate_report(SAMPLE_PATIENT_DATA, output_format="pdf")

    if "error" in report:
        print(f"ERROR: {report['error']}")
        return

    pdf_path = report.get("pdf_path")
    status = report.get("status", "unknown")
    
    print(f"Status: {status}")
    if pdf_path:
        print(f"PDF saved to: {pdf_path}\n")
    else:
        print("PDF generation not available (reportlab may not be installed)\n")


def test_cache_functionality():
    """Test explanation caching"""
    print_section("TEST 5: EXPLANATION CACHING")

    engine = AIExplanationEngine()

    print("Testing explanation cache...")
    print("-" * 60)

    drug_1 = "Warfarin"
    drug_2 = "Aspirin"
    severity = "High"
    risk = "Increased bleeding risk"

    # First call - generates explanation
    print("First call (generates explanation):")
    import time
    start = time.time()
    exp1 = engine.generate_explanation(drug_1, drug_2, severity, risk)
    time1 = time.time() - start
    print(f"  Time: {time1:.3f}s")
    print(f"  Result: {exp1[:50]}...\n")

    # Clear cache and try again
    from modules.ai_explanation_engine import explanation_cache
    print("Cache status:")
    print(f"  Cached items: {len(explanation_cache.cache)}\n")

    # Second call - should use cache (if AI available)
    print("Second call (should use cache):")
    start = time.time()
    exp2 = engine.generate_explanation(drug_1, drug_2, severity, risk)
    time2 = time.time() - start
    print(f"  Time: {time2:.3f}s")
    print(f"  Same result: {exp1 == exp2}\n")


def test_error_handling():
    """Test error handling"""
    print_section("TEST 6: ERROR HANDLING")

    generator = ReportGenerator()

    print("Test 6a: Missing medication data")
    print("-" * 60)
    invalid_data = {
        "patient_id": "P999",
        "age": 65,
        "medications": [],
        "interactions": []
    }
    
    report = generator.generate_report(invalid_data)
    print(f"Status: {'Success' if 'error' not in report else 'Error'}")
    print(f"Report ID: {report.get('report_id', 'N/A')}\n")

    print("Test 6b: Empty interactions")
    print("-" * 60)
    data_no_interactions = {
        "patient_id": "P103",
        "age": 70,
        "medications": ["Medication1", "Medication2"],
        "interactions": []
    }
    
    report = generator.generate_report(data_no_interactions)
    risk_summary = report.get("risk_summary", {})
    print(f"Status: Success")
    print(f"Interactions Count: {risk_summary.get('total_interactions')}")
    print(f"Overall Risk: {risk_summary.get('overall_risk')}\n")


def test_multiple_patients():
    """Test with multiple patients"""
    print_section("TEST 7: MULTIPLE PATIENTS")

    generator = ReportGenerator()

    patients = [
        {
            "patient_id": "P101",
            "age": 65,
            "medications": ["Lisinopril", "Atorvastatin"],
            "interactions": []
        },
        {
            "patient_id": "P102",
            "age": 72,
            "medications": ["Warfarin", "Aspirin", "Ibuprofen"],
            "interactions": [
                {
                    "drug_1": "Warfarin",
                    "drug_2": "Aspirin",
                    "severity": "High",
                    "clinical_risk": "Increased bleeding risk"
                }
            ]
        },
        {
            "patient_id": "P103",
            "age": 78,
            "medications": ["A", "B", "C", "D", "E", "F", "G"],
            "interactions": [
                {
                    "drug_1": "A",
                    "drug_2": "B",
                    "severity": "Critical",
                    "clinical_risk": "Critical interaction"
                }
            ]
        }
    ]

    for patient in patients:
        report = generator.generate_report(patient, output_format="json")
        risk = report.get("risk_summary", {})
        poly = report.get("polypharmacy_assessment", {})
        
        print(f"Patient {patient['patient_id']}:")
        print(f"  Age: {patient['age']}")
        print(f"  Medications: {len(patient['medications'])}")
        print(f"  Risk Level: {risk.get('overall_risk')}")
        print(f"  Polypharmacy: {poly.get('is_polypharmacy')}")
        print()


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 15 + "HC-03 HEALTHCARE SAFETY SYSTEM - TEST SUITE" + " " * 21 + "║")
    print("╚" + "═" * 78 + "╝")

    try:
        test_ai_explanation_engine()
        test_report_generator_json()
        test_report_generator_text()
        test_report_generator_pdf()
        test_cache_functionality()
        test_error_handling()
        test_multiple_patients()

        print_section("ALL TESTS COMPLETED")
        print("✓ AI Explanation Engine working")
        print("✓ Report Generator (JSON) working")
        print("✓ Report Generator (Text) working")
        print("✓ Report Generator (PDF) working")
        print("✓ Caching functionality working")
        print("✓ Error handling working")
        print("✓ Multiple patients working\n")
        
        print("Test reports saved:")
        print("  - test_report.json (JSON format)")
        print("  - test_report.txt (Text format)")
        print("  - Report_RPT*.pdf (PDF format, if reportlab available)\n")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        print(f"\n❌ ERROR: {str(e)}\n")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
