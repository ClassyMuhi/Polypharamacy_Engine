"""
HC-03 System Configuration File
Centralized settings for the Healthcare Safety System
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key-here")
LLM_MODEL = "gpt-3.5-turbo"  # Can be changed to gpt-4 for better results
LLM_TEMPERATURE = 0.7

# Application Configuration
DEBUG_MODE = os.getenv("DEBUG_MODE", "True").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Report Configuration
REPORT_FORMAT_DEFAULT = "json"  # json, pdf, text
PDF_FONT_SIZE = 12
PDF_LINE_SPACING = 1.5

# Polypharmacy Threshold
POLYPHARMACY_THRESHOLD = 5  # Medicines that constitute polypharmacy

# Severity Levels
SEVERITY_LEVELS = {
    "Critical": 4,
    "High": 3,
    "Moderate": 2,
    "Low": 1
}

# Color coding for severity (for PDF/HTML)
SEVERITY_COLORS = {
    "Critical": "#DC143C",  # Crimson
    "High": "#FF6347",      # Tomato
    "Moderate": "#FFD700",  # Gold
    "Low": "#90EE90"        # Light Green
}

# Fast API Configuration
FASTAPI_HOST = "127.0.0.1"
FASTAPI_PORT = 8000
FASTAPI_RELOAD = True

# Clinical Recommendations Templates
CLINICAL_RECOMMENDATIONS = {
    "High": [
        "Immediate clinical review required",
        "Consider alternative medications",
        "Monitor patient closely for adverse events",
        "Consult with clinical pharmacist"
    ],
    "Moderate": [
        "Review medication timing",
        "Monitor for interaction signs",
        "Patient education advised"
    ],
    "Low": [
        "Continue routine monitoring",
        "Document in patient records"
    ]
}

# Logging Configuration
LOGGING_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = "hc03_system.log"

if __name__ == "__main__":
    print("HC-03 System Configuration Loaded")
    print(f"Debug Mode: {DEBUG_MODE}")
    print(f"LLM Model: {LLM_MODEL}")
