# HC-03: Medicine Interaction & Polypharmacy Risk Checker

**Advanced AI-powered medication safety analysis system for elderly patient care**

---

## 📋 Overview

HC-03 is a healthcare safety system designed to analyze medication interactions and polypharmacy risks for elderly patients. It combines clinical pharmacology knowledge with AI-powered explanations to provide doctors with actionable safety insights.

### Key Features

✅ **Drug Interaction Detection** - Identifies and severities drug interactions  
✅ **Polypharmacy Assessment** - Evaluates risks from multiple medications  
✅ **AI-Powered Explanations** - Converts technical data into clinical insights  
✅ **Multi-Format Reports** - JSON, Text, and PDF output formats  
✅ **Clinical Recommendations** - Tailored advice based on severity levels  
✅ **RESTful API** - Easy integration with existing systems  
✅ **Production-Ready** - Logging, error handling, type hints, caching

---

## 🏗️ Project Structure

```
hc03_system/
├── app.py                          # FastAPI application
├── config.py                       # Configuration settings
├── test_runner.py                  # Comprehensive test suite
├── requirements.txt                # Python dependencies
│
├── modules/
│   ├── report_generator.py         # Report generation logic
│   └── ai_explanation_engine.py    # AI explanation engine
│
├── utils/
│   ├── formatter.py                # Text formatting utilities
│   └── pdf_exporter.py             # PDF export functionality
│
├── data/
│   └── sample_interaction.json     # Sample test data
│
└── logs/
    └── hc03_system.log             # System logs
```

---

## 🚀 Quick Start

### 1. **Install Python 3.9+**

Ensure you have Python 3.9 or later installed.

### 2. **Setup Virtual Environment** (Recommended)

```bash
# Navigate to hc03_system directory
cd hc03_system

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. **Install Dependencies**

```bash
pip install -r requirements.txt
```

### 4. **Configure OpenAI API (Optional but Recommended)**

For AI-powered explanations, set your OpenAI API key:

```bash
# Create .env file in hc03_system directory
echo OPENAI_API_KEY=your-api-key-here > .env
```

The system will work without an API key (using fallback explanations).

### 5. **Run Tests**

```bash
python test_runner.py
```

This runs comprehensive tests on all modules and generates sample reports.

### 6. **Start the API Server**

```bash
python app.py
```

The API will be available at `http://127.0.0.1:8000`

### 7. **Access Interactive Documentation**

Open your browser and go to:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

---

## 📦 Module Details

### **Module 1: Report Generator** (`modules/report_generator.py`)

Generates comprehensive medication safety reports.

#### Key Functions:

```python
generate_report(patient_data, output_format="json")
```
- Accepts patient medication data with interactions
- Returns formatted report (JSON/Text/PDF)
- Includes AI explanations for each interaction
- Calculates polypharmacy risks
- Generates clinical recommendations

#### Example Usage:

```python
from modules.report_generator import ReportGenerator

generator = ReportGenerator()

patient_data = {
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
}

report = generator.generate_report(patient_data, output_format="json")
```

### **Module 2: AI Explanation Engine** (`modules/ai_explanation_engine.py`)

Converts technical drug interactions into clear clinical explanations.

#### Key Functions:

```python
generate_explanation(drug_1, drug_2, severity, clinical_risk)
generate_polypharmacy_warning(medication_count)
```

#### Example Usage:

```python
from modules.ai_explanation_engine import AIExplanationEngine

engine = AIExplanationEngine()

# Get explanation for interaction
explanation = engine.generate_explanation(
    drug_1="Warfarin",
    drug_2="Aspirin",
    severity="High",
    clinical_risk="Increased bleeding risk"
)

# Get polypharmacy warning
warning = engine.generate_polypharmacy_warning(medication_count=7)
```

---

## 📡 API Endpoints

### 1. **Health Check**

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "HC-03",
  "ai_engine": "available",
  "timestamp": "2024-01-15T10:30:00"
}
```

### 2. **Generate Report**

```http
POST /generate-report
```

**Request Body:**
```json
{
  "patient_data": {
    "patient_id": "P102",
    "age": 72,
    "medications": ["Warfarin", "Aspirin", "Ibuprofen", "Metformin"],
    "interactions": [
      {
        "drug_1": "Warfarin",
        "drug_2": "Aspirin",
        "severity": "High",
        "clinical_risk": "Increased bleeding risk"
      },
      {
        "drug_1": "Aspirin",
        "drug_2": "Ibuprofen",
        "severity": "Moderate",
        "clinical_risk": "Reduced antiplatelet effect"
      }
    ]
  },
  "output_format": "json"
}
```

**Response (Abbreviated):**
```json
{
  "status": "success",
  "data": {
    "report_id": "RPT20240115103045",
    "generated_at": "2024-01-15T10:30:45.123456",
    "patient_summary": {
      "patient_id": "P102",
      "age": 72,
      "medication_count": 4,
      "interaction_count": 2
    },
    "risk_summary": {
      "total_interactions": 2,
      "critical_count": 0,
      "high_count": 1,
      "moderate_count": 1,
      "overall_risk": "High"
    },
    "interactions": [
      {
        "drug_1": "Warfarin",
        "drug_2": "Aspirin",
        "severity": "High",
        "clinical_risk": "Increased bleeding risk",
        "ai_explanation": "Warfarin and Aspirin both affect blood clotting..."
      }
    ],
    "polypharmacy_assessment": {
      "is_polypharmacy": false,
      "medication_count": 4,
      "threshold": 5,
      "risk_level": "Low"
    },
    "clinical_recommendations": [
      "Immediate clinical review required",
      "Consider alternative medications"
    ]
  }
}
```

### 3. **Explain Drug Interaction**

```http
POST /explain-interaction
```

**Request Body:**
```json
{
  "drug_1": "Warfarin",
  "drug_2": "Aspirin",
  "severity": "High",
  "clinical_risk": "Increased bleeding risk"
}
```

**Response:**
```json
{
  "status": "success",
  "interaction": {
    "drug_1": "Warfarin",
    "drug_2": "Aspirin",
    "severity": "High",
    "clinical_risk": "Increased bleeding risk"
  },
  "explanation": "Warfarin and Aspirin both affect blood clotting. When taken together, they can significantly increase the risk of bleeding, especially in elderly patients. Doctors should carefully monitor the patient or consider alternative medications.",
  "timestamp": "2024-01-15T10:35:22"
}
```

### 4. **Polypharmacy Warning**

```http
POST /polypharmacy-warning?medication_count=7
```

**Response:**
```json
{
  "status": "success",
  "medication_count": 7,
  "warning": "HIGH RISK: Patient is taking 7 medications (moderate-to-high polypharmacy)...",
  "timestamp": "2024-01-15T10:40:15"
}
```

---

## 🧪 Example API Requests

### Using cURL

```bash
# Health check
curl http://127.0.0.1:8000/health

# Generate report
curl -X POST http://127.0.0.1:8000/generate-report \
  -H "Content-Type: application/json" \
  -d @request.json

# Explain interaction
curl -X POST http://127.0.0.1:8000/explain-interaction \
  -H "Content-Type: application/json" \
  -d '{
    "drug_1": "Warfarin",
    "drug_2": "Aspirin",
    "severity": "High",
    "clinical_risk": "Increased bleeding risk"
  }'

# Polypharmacy warning
curl -X POST "http://127.0.0.1:8000/polypharmacy-warning?medication_count=7"
```

### Using Python Requests

```python
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# Generate report
payload = {
    "patient_data": {
        "patient_id": "P102",
        "age": 72,
        "medications": ["Warfarin", "Aspirin"],
        "interactions": [{
            "drug_1": "Warfarin",
            "drug_2": "Aspirin",
            "severity": "High",
            "clinical_risk": "Increased bleeding risk"
        }]
    },
    "output_format": "json"
}

response = requests.post(
    f"{BASE_URL}/generate-report",
    json=payload
)

report = response.json()
print(json.dumps(report, indent=2))
```

### Using Postman

1. Open Postman
2. Create new POST request to `http://127.0.0.1:8000/generate-report`
3. Set Header: `Content-Type: application/json`
4. Use the request body from examples above
5. Send request

---

## 📄 Understanding Report Output

### Report Sections

#### 1. **Patient Summary**
- Patient ID, age, medication count
- Number of documented interactions

#### 2. **Medication List**
- All medications with count
- Polypharmacy status

#### 3. **Interaction Risk Summary**
- Breakdown by severity: Critical, High, Moderate, Low
- Overall risk determination

#### 4. **Drug Interaction Details**
- Drug pairs with severity levels
- Clinical risks
- AI-powered explanations
- Severity indicators

#### 5. **Polypharmacy Assessment**
- Is polypharmacy status
- Risk level based on medication count
- AI-generated warning

#### 6. **Clinical Recommendations**
- Actionable recommendations for clinicians
- Based on severity and interaction types

---

## ⚙️ Configuration

### `config.py` Settings

```python
# AI Model Configuration
OPENAI_API_KEY = "your-key-here"
LLM_MODEL = "gpt-3.5-turbo"  # or gpt-4
LLM_TEMPERATURE = 0.7

# Application
DEBUG_MODE = True
LOG_LEVEL = "INFO"

# Polypharmacy
POLYPHARMACY_THRESHOLD = 5  # medications that trigger polypharmacy alert

# Report Defaults
REPORT_FORMAT_DEFAULT = "json"
```

---

## 🔍 Text Report Example

```
================================================================================
MEDICATION SAFETY REPORT - HC-03
================================================================================

Report ID: RPT20240115103045
Generated: 2024-01-15 10:30:45

------
PATIENT SUMMARY
------
Patient ID: P102
Age: 72
Medications: 4
Documented Interactions: 2

------
MEDICATION LIST
------
Total Medications: 4

• Warfarin
• Aspirin
• Ibuprofen
• Metformin

------
INTERACTION RISK SUMMARY
------
Total Interactions: 2
Critical: 0 🔴
High: 1 🟠
Moderate: 1 🟡
Low: 0 🟢
Overall Risk Level: High

------
DRUG INTERACTION DETAILS
------

1. Warfarin + Aspirin
   Severity: High 🟠
   Clinical Risk: Increased bleeding risk
   Explanation: Warfarin and Aspirin both affect blood clotting. When taken...

2. Aspirin + Ibuprofen
   Severity: Moderate 🟡
   Clinical Risk: Reduced antiplatelet effect
   Explanation: NSAIDs can reduce the antiplatelet effects of aspirin...

------
POLYPHARMACY ASSESSMENT
------
Polypharmacy Status: NO
Medications: 4 (Threshold: 5)
Risk Level: Low

Assessment: Patient is taking 4 medications. Below polypharmacy threshold.

------
CLINICAL RECOMMENDATIONS
------
• Immediate clinical review required
• Consider alternative medications
• Monitor patient closely for adverse events
• Consult with clinical pharmacist

================================================================================
This report is for clinical decision support only.
Always consult clinical pharmacist or physician.
================================================================================
```

---

## 🚨 Error Handling

The system includes comprehensive error handling:

```python
# Invalid request format
{"status": "error", "detail": "validation error", "timestamp": "..."}

# Unsupported operation
{"status": "error", "detail": "Operation not supported", "timestamp": "..."}

# Server error
{"status": "error", "detail": "Internal server error", "timestamp": "..."}
```

---

## 📊 Severity Levels

| Level | Code | Description | Action |
|-------|------|-------------|--------|
| **Critical** | 🔴 | Immediate clinical review needed | Stop one medication, urgent consultation |
| **High** | 🟠 | Significant interaction | Review medications, close monitoring |
| **Moderate** | 🟡 | Notable interaction | Monitor for symptoms, consider adjustment |
| **Low** | 🟢 | Minor interaction | Document, routine monitoring |

---

## 🔐 Security Considerations

When deploying in production:

1. **Store API keys securely** - Use environment variables or secret management
2. **Use HTTPS** - Enable SSL/TLS encryption
3. **Implement authentication** - Add JWT or OAuth2 tokens
4. **Rate limiting** - Prevent API abuse
5. **Data encryption** - Protect patient information in transit and at rest
6. **HIPAA compliance** - Ensure PHI protection (if US healthcare)
7. **Audit logging** - Track all access and modifications

---

## 📝 Logging

All system activities are logged to `hc03_system.log`:

```
2024-01-15 10:30:45 - modules.report_generator - INFO - Generating report for patient P102
2024-01-15 10:30:46 - modules.ai_explanation_engine - INFO - Generated explanation for Warfarin + Aspirin
2024-01-15 10:30:47 - app - INFO - Report generated successfully for P102
```

---

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_runner.py
```

Tests include:
- AI Explanation Engine
- Report Generation (JSON, Text, PDF)
- Caching functionality
- Error handling
- Multiple patient scenarios

---

## 📚 Dependencies

- **FastAPI** - Modern web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **OpenAI** - LLM integration (optional)
- **ReportLab** - PDF generation
- **Python-dotenv** - Environment configuration

---

## 🔧 Development

### Adding New Features

1. **Custom drug interactions** - Add to data files
2. **New severity levels** - Update config.py
3. **Additional report formats** - Extend report_generator.py
4. **Custom explanations** - Modify ai_explanation_engine.py

### Extending the System

```python
# Add custom interaction explanation
def add_custom_explanation(drug_1, drug_2, explanation):
    explanation_cache.set(drug_1, drug_2, "Custom", explanation)

# Add new recommendation
CLINICAL_RECOMMENDATIONS["VeryHigh"] = [
    "Emergency consultation required"
]
```

---

## 🐛 Troubleshooting

**Problem: "OpenAI API key not found"**
- Solution: Set OPENAI_API_KEY environment variable or create .env file

**Problem: "reportlab not available"**
- Solution: `pip install reportlab` for PDF export

**Problem: "Port 8000 already in use"**
- Solution: Change port in config.py or use `python app.py --port 8001`

**Problem: "Module not found"**
- Solution: Ensure you're in the hc03_system directory and venv is activated

---

## 📞 Support & Documentation

- **API Docs**: Visit `http://localhost:8000/docs` when server is running
- **Source Code**: All files are well-documented with docstrings
- **Tests**: See `test_runner.py` for usage examples
- **Logs**: Check `hc03_system.log` for detailed system information

---

## 📄 License

This system is for healthcare research and educational purposes.

---

## 👨‍⚕️ Disclaimer

**This system is designed for clinical decision support only.** It is not a substitute for professional medical judgment. Always consult with qualified healthcare professionals before making medication decisions.

---

**Last Updated**: January 2024  
**Version**: 1.0.0  
**Author**: HC-03 Development Team
