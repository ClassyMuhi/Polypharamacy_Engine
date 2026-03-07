"""
HC-03 Healthcare Safety System - FastAPI Application
Main API for medicine interaction and polypharmacy risk analysis
"""

import logging
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from modules.report_generator import ReportGenerator
from modules.ai_explanation_engine import AIExplanationEngine
from config import (
    FASTAPI_HOST, FASTAPI_PORT, FASTAPI_RELOAD, DEBUG_MODE,
    LOG_LEVEL, LOGGING_FORMAT, LOG_FILE
)

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOGGING_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="HC-03: Medicine Interaction & Polypharmacy Risk Checker",
    description="AI-powered medication safety analysis for elderly patient care",
    version="1.0.0",
    docs_url=None,  # Disable Swagger UI
    redoc_url=None,  # Disable ReDoc UI
    openapi_url=None  # Disable OpenAPI schema endpoint
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize modules
report_generator = ReportGenerator()
ai_engine = AIExplanationEngine()


# ==================== Pydantic Models ====================

class DrugInteraction(BaseModel):
    """Model for drug interaction data"""
    drug_1: str = Field(..., description="First drug name")
    drug_2: str = Field(..., description="Second drug name")
    severity: str = Field(..., description="Severity level (Low/Moderate/High/Critical)")
    clinical_risk: str = Field(..., description="Clinical risk description")


class PatientMedicationData(BaseModel):
    """Model for patient medication data"""
    patient_id: str = Field(..., description="Unique patient identifier")
    age: int = Field(..., description="Patient age")
    medications: List[str] = Field(..., description="List of medications")
    interactions: List[DrugInteraction] = Field(..., description="Detected drug interactions")


class ExplanationRequest(BaseModel):
    """Model for explanation request"""
    drug_1: str = Field(..., description="First drug name")
    drug_2: str = Field(..., description="Second drug name")
    severity: str = Field(default="High", description="Severity level")
    clinical_risk: str = Field(..., description="Clinical risk description")


class ReportRequest(BaseModel):
    """Model for report generation request"""
    patient_data: PatientMedicationData = Field(..., description="Patient medication data")
    output_format: str = Field(default="json", description="Output format (json/text/pdf)")


# ==================== API Endpoints ====================

@app.get("/", tags=["Health"])
async def root():
    """API root - health check"""
    return {
        "status": "active",
        "service": "HC-03 Medicine Interaction & Polypharmacy Risk Checker",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "HC-03",
        "ai_engine": "available" if ai_engine.available else "fallback",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/generate-report", tags=["Reports"])
async def generate_report(request: ReportRequest):
    """
    Generate comprehensive medication safety report
    
    Returns structured safety report with:
    - Patient summary
    - Medication list
    - Drug interaction alerts
    - Polypharmacy assessment
    - AI-powered explanations
    - Clinical recommendations
    """
    try:
        logger.info(f"Generating report for patient {request.patient_data.patient_id}")

        # Convert Pydantic models to dicts
        patient_dict = request.patient_data.dict()
        patient_dict["interactions"] = [
            interaction.dict() for interaction in request.patient_data.interactions
        ]

        # Generate report
        report = report_generator.generate_report(
            patient_dict,
            output_format=request.output_format
        )

        if "error" in report:
            raise HTTPException(status_code=500, detail=report["error"])

        logger.info(f"Report generated successfully for {request.patient_data.patient_id}")
        return {
            "status": "success",
            "data": report,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/explain-interaction", tags=["AI Engine"])
async def explain_interaction(request: ExplanationRequest):
    """
    Generate AI explanation for a drug interaction
    
    Converts technical alert into clear clinical explanation
    suitable for doctor review.
    """
    try:
        logger.info(f"Generating explanation for {request.drug_1} + {request.drug_2}")

        explanation = ai_engine.generate_explanation(
            drug_1=request.drug_1,
            drug_2=request.drug_2,
            severity=request.severity,
            clinical_risk=request.clinical_risk
        )

        logger.info(f"Explanation generated successfully")
        return {
            "status": "success",
            "interaction": {
                "drug_1": request.drug_1,
                "drug_2": request.drug_2,
                "severity": request.severity,
                "clinical_risk": request.clinical_risk
            },
            "explanation": explanation,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error generating explanation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/polypharmacy-warning", tags=["AI Engine"])
async def polypharmacy_warning(medication_count: int):
    """
    Generate polypharmacy warning for multiple medications
    
    Provides clinical warning about risks associated with
    taking multiple medications simultaneously.
    """
    try:
        logger.info(f"Generating polypharmacy warning for {medication_count} medications")

        warning = ai_engine.generate_polypharmacy_warning(medication_count)

        logger.info("Polypharmacy warning generated successfully")
        return {
            "status": "success",
            "medication_count": medication_count,
            "warning": warning,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error generating polypharmacy warning: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/report/{report_id}", tags=["Reports"])
async def get_report(report_id: str):
    """
    Retrieve a previously generated report
    (In production, would fetch from database)
    """
    try:
        if not report_generator.report_data:
            raise HTTPException(
                status_code=404,
                detail=f"Report {report_id} not found"
            )

        return {
            "status": "success",
            "report": report_generator.report_data,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error retrieving report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/docs", tags=["API"])
async def api_documentation():
    """API documentation endpoint"""
    return {
        "service": "HC-03 Medicine Interaction & Polypharmacy Risk Checker",
        "endpoints": {
            "POST /generate-report": "Generate comprehensive medication safety report",
            "POST /explain-interaction": "Get AI explanation for drug interaction",
            "POST /polypharmacy-warning": "Get warning for polypharmacy",
            "GET /health": "Health check",
            "GET /docs": "This documentation"
        },
        "documentation": "Visit /docs for interactive API documentation"
    }


# ==================== Error Handlers ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "detail": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "detail": "Internal server error",
            "timestamp": datetime.now().isoformat()
        }
    )


# ==================== Startup/Shutdown ====================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("=" * 80)
    logger.info("HC-03 Healthcare Safety System Starting")
    logger.info("=" * 80)
    logger.info(f"Debug Mode: {DEBUG_MODE}")
    logger.info(f"AI Engine Available: {ai_engine.available}")
    logger.info(f"API running on {FASTAPI_HOST}:{FASTAPI_PORT}")
    logger.info("=" * 80)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("HC-03 System Shutting Down")


# ==================== Main ====================

if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting HC-03 API Server on {FASTAPI_HOST}:{FASTAPI_PORT}")

    uvicorn.run(
        "app:app",
        host=FASTAPI_HOST,
        port=FASTAPI_PORT,
        reload=FASTAPI_RELOAD,
        log_level=LOG_LEVEL.lower()
    )
