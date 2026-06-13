# Polypharmacy Engine

A comprehensive Python-based system for analyzing drug-drug interactions and assessing polypharmacy risks in patient medication profiles. This engine integrates prescription OCR, medicine parsing, interaction checking, and clinical report generation.

## Overview

The Polypharmacy Engine is designed to help healthcare professionals identify dangerous drug combinations and assess polypharmacy risks (≥5 medications). It combines multiple modules including:

- **Prescription OCR**: Extracts medication information from prescription images using Google Gemini API
- **Medicine Parser**: Normalizes and validates medicine names
- **Interaction Engine**: Checks for drug-drug interactions against a comprehensive database
- **Risk Calculator**: Calculates polypharmacy risk scores based on patient profile
- **Report Generator**: Creates clinical reports in text and PDF formats

## Features

- 🔍 **Drug Interaction Detection**: Identifies HIGH, MODERATE, and LOW severity drug interactions
- ⚠️ **Polypharmacy Risk Assessment**: Detects when patients are on 5+ medications
- 📸 **OCR Prescription Processing**: Extracts medicines from prescription images
- 📊 **Clinical Report Generation**: Generates detailed clinical reports in multiple formats
- 🗄️ **Comprehensive Drug Database**: Built-in database of common drug interactions
- 🔧 **Configurable Settings**: Easy environment-based configuration

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Google Gemini API key (for OCR functionality)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/ClassyMuhi/Polypharamacy_Engine.git
cd Polypharamacy_Engine
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with your API keys:
```bash
cp .env.example .env
```

4. Add your credentials to `.env`:
```
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
OPENAI_API_KEY=your_openai_api_key_here
DEBUG_MODE=True
```

## Usage

### Basic Drug Interaction Checking

```python
from MedicineInteractionChecker.patient import Patient
from MedicineInteractionChecker.interaction_engine import InteractionEngine

# Create a patient
patient = Patient("John Doe", age=72)

# Add medications
patient.add_medication("Warfarin")
patient.add_medication("Aspirin")
patient.add_medication("Ibuprofen")

# Initialize the interaction engine
engine = InteractionEngine()

# Check for interactions and print report
engine.check_interactions(patient)
```

**Output:**
```
Patient Profile: John Doe (Age: 72)
Medications: ['Warfarin', 'Aspirin', 'Ibuprofen']

--- Drug Interaction Report ---

  [!!HIGH!!] Interaction Detected:
       Warfarin + Aspirin
       Severity    : HIGH
       Description : Serious bleeding risk: both inhibit clotting

  [!!HIGH!!] Interaction Detected:
       Warfarin + Ibuprofen
       Severity    : HIGH
       Description : Ibuprofen displaces Warfarin, raising bleeding risk

  [WARNING] Polypharmacy Risk Detected: John Doe is taking 3 medications (>= 5).
          Please consult a clinical pharmacist for a medication review.

--- End of Report ---
```

### Full Pipeline Test

Run the complete pipeline including OCR, parsing, interaction checking, and report generation:

```bash
python run_full_pipeline_test.py
```

This will:
1. Extract medicines from a prescription image using OCR
2. Parse and normalize medicine names
3. Check for drug interactions
4. Calculate polypharmacy risk score
5. Generate a clinical report (text and PDF)

### Quick Interaction Check

```python
from interaction_engine import check_interactions

# Simple interaction check without patient object
medications = ["Warfarin", "Aspirin", "Ibuprofen"]
results = check_interactions(medications, db_path='interactions.json')

for warning in results:
    print(warning)
```

### Programmatic Integration

```python
from MedicineInteractionChecker.interaction_engine import InteractionEngine
from MedicineInteractionChecker.patient import Patient
from itertools import combinations

# Create patient and engine
patient = Patient("Jane Smith", age=65)
engine = InteractionEngine()

# Add multiple medications
medications = ["Aspirin", "Warfarin", "Ibuprofen", "Metformin", "Amoxicillin"]
for med in medications:
    patient.add_medication(med)

# Find specific interactions
interactions = []
for med_a, med_b in combinations(medications, 2):
    interaction = engine._find_interaction(med_a, med_b)
    if interaction:
        interactions.append({
            "drug_1": med_a,
            "drug_2": med_b,
            "severity": interaction.severity.name,
            "description": interaction.description
        })

# Process interactions
for inter in interactions:
    print(f"{inter['severity']}: {inter['drug_1']} + {inter['drug_2']}")
    print(f"  → {inter['description']}\n")
```

## Database Schema

### Supported Drug Interactions

The system includes pre-configured interactions across severity levels:

**HIGH Severity** (Serious health risk)
- Aspirin + Warfarin → Serious bleeding risk
- Warfarin + Ibuprofen → Raises bleeding risk
- Metformin + Ibuprofen → Increases Metformin toxicity

**MODERATE Severity** (Notable interactions)
- Aspirin + Ibuprofen → Increased GI bleeding risk
- Warfarin + Amoxicillin → Potentiates Warfarin

**LOW Severity** (Monitor)
- Paracetamol + Warfarin → Mild enhancement of anticoagulation
- Atorvastatin + Paracetamol → Usually well tolerated

## Configuration

Key settings in `config.py`:

- `GEMINI_API_KEY`: Google Gemini API key for OCR
- `GEMINI_MODEL`: Model version (default: gemini-2.5-flash)
- `POLYPHARMACY_THRESHOLD`: Number of meds to trigger polypharmacy alert (default: 5)

## Project Structure

```
Polypharamacy_Engine/
├── MedicineInteractionChecker/
│   ├── interaction_engine.py     # Core interaction checking logic
│   ├── patient.py                # Patient data model
│   ├── drug.py                   # Drug interaction record
│   └── ...
├── modules/
│   ├── ocr_model/                # OCR and medicine parsing
│   ├── polypharmacy_risk_engine/  # Risk calculation
│   └── ...
├── hc03_system/                  # Clinical report generation
├── interactions.json             # Drug interaction database
├── config.py                     # Configuration management
├── run_full_pipeline_test.py     # Full pipeline test script
└── README.md                     # This file
```

## Testing

Run the test pipeline:

```bash
python run_full_pipeline_test.py
```

This will generate a `test_report.json` with comprehensive test results.

## API Response Format

Typical interaction check response:

```json
{
  "patient_id": "P_PIPELINE_TEST",
  "medications": ["Aspirin", "Warfarin", "Ibuprofen"],
  "interactions": [
    {
      "drug_1": "Warfarin",
      "drug_2": "Aspirin",
      "severity": "HIGH",
      "clinical_risk": "Serious bleeding risk: both inhibit clotting"
    }
  ],
  "polypharmacy_risk": {
    "risk_score": 45,
    "risk_category": "MODERATE",
    "medications_count": 3
  }
}
```

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

This project is provided as-is for educational and healthcare research purposes.

## Support

For questions or issues, please open a [GitHub Issue](https://github.com/ClassyMuhi/Polypharamacy_Engine/issues).

## Disclaimer

⚠️ **Medical Disclaimer**: This tool is designed to assist healthcare professionals in identifying potential drug interactions and should not replace professional clinical judgment. Always consult with qualified healthcare providers and clinical pharmacists for medical decisions.

## Acknowledgments

- Built with Python and modern healthcare informatics best practices
- Integrates Google Gemini API for OCR capabilities
- Designed following clinical polypharmacy guidelines
