"""
Report Generator Module
Generates structured medical safety reports from interaction data
"""

import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from modules.ai_explanation_engine import AIExplanationEngine, explanation_cache
from utils.formatter import (
    TextFormatter, DataFormatter, ReportBuilder, severity_to_emoji
)
from utils.pdf_exporter import PDFExporter
from config import POLYPHARMACY_THRESHOLD, SEVERITY_LEVELS, CLINICAL_RECOMMENDATIONS

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates comprehensive medication safety reports"""

    def __init__(self, ai_engine: Optional[AIExplanationEngine] = None):
        """
        Initialize Report Generator
        Args:
            ai_engine: AI Explanation Engine instance (creates new if None)
        """
        self.ai_engine = ai_engine or AIExplanationEngine()
        self.report_data: Dict[str, Any] = {}

    def generate_report(
        self,
        patient_data: Dict[str, Any],
        output_format: str = "json"
    ) -> Dict[str, Any]:
        """
        Generate complete report from patient data
        Args:
            patient_data: Patient interaction data
            output_format: Output format (json, text, pdf)
        Returns:
            Report data dictionary
        """
        logger.info(f"Generating report for patient {patient_data.get('patient_id')}")

        try:
            # Build report structure
            report = {
                "report_id": self._generate_report_id(),
                "generated_at": datetime.now().isoformat(),
                "patient_summary": self._create_patient_summary(patient_data),
                "medication_list": self._format_medications(patient_data.get("medications", [])),
                "interactions": self._format_interactions_with_explanations(
                    patient_data.get("interactions", [])
                ),
                "polypharmacy_assessment": self._assess_polypharmacy(
                    patient_data.get("medications", [])
                ),
                "clinical_recommendations": self._generate_clinical_recommendations(
                    patient_data.get("interactions", [])
                ),
                "risk_summary": self._calculate_risk_summary(patient_data.get("interactions", []))
            }

            self.report_data = report

            # Convert to requested format
            if output_format.lower() == "json":
                return report
            elif output_format.lower() == "text":
                return {"formatted_report": self._to_text_report(report)}
            elif output_format.lower() == "pdf":
                pdf_path = self._to_pdf_report(report)
                return {"pdf_path": pdf_path, "status": "success"}
            else:
                logger.warning(f"Unknown format: {output_format}. Returning JSON.")
                return report

        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return {"error": str(e), "status": "failed"}

    def _create_patient_summary(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create patient information summary"""
        return {
            "patient_id": patient_data.get("patient_id", "N/A"),
            "age": patient_data.get("age", "N/A"),
            "medication_count": len(patient_data.get("medications", [])),
            "interaction_count": len(patient_data.get("interactions", [])),
            "report_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def _format_medications(self, medications: List[str]) -> Dict[str, Any]:
        """Format medication list with metadata"""
        return {
            "total_count": len(medications),
            "medications": medications,
            "is_polypharmacy": len(medications) >= POLYPHARMACY_THRESHOLD
        }

    def _format_interactions_with_explanations(
        self,
        interactions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Format interactions with AI explanations
        Args:
            interactions: List of interaction dictionaries
        Returns:
            Formatted interactions with explanations
        """
        formatted_interactions = []

        for interaction in interactions:
            drug_1 = interaction.get("drug_1", "")
            drug_2 = interaction.get("drug_2", "")
            severity = interaction.get("severity", "Low")
            clinical_risk = interaction.get("clinical_risk", "")

            # Check cache first
            cached_explanation = explanation_cache.get(drug_1, drug_2, severity)
            
            if cached_explanation:
                explanation = cached_explanation
            else:
                # Generate new explanation
                explanation = self.ai_engine.generate_explanation(
                    drug_1, drug_2, severity, clinical_risk
                )
                # Cache it
                explanation_cache.set(drug_1, drug_2, severity, explanation)

            formatted_interactions.append({
                "drug_1": drug_1,
                "drug_2": drug_2,
                "severity": severity,
                "severity_level": SEVERITY_LEVELS.get(severity, 1),
                "clinical_risk": clinical_risk,
                "ai_explanation": explanation,
                "severity_emoji": severity_to_emoji(severity)
            })

        # Sort by severity level (descending)
        formatted_interactions.sort(key=lambda x: x["severity_level"], reverse=True)
        return formatted_interactions

    def _assess_polypharmacy(self, medications: List[str]) -> Dict[str, Any]:
        """Assess and generate warning for polypharmacy"""
        med_count = len(medications)
        is_polypharmacy = med_count >= POLYPHARMACY_THRESHOLD

        if is_polypharmacy:
            warning = self.ai_engine.generate_polypharmacy_warning(med_count)
        else:
            warning = f"Patient is taking {med_count} medications. Below polypharmacy threshold."

        return {
            "is_polypharmacy": is_polypharmacy,
            "medication_count": med_count,
            "threshold": POLYPHARMACY_THRESHOLD,
            "risk_level": self._get_risk_level(med_count),
            "warning": warning
        }

    def _get_risk_level(self, med_count: int) -> str:
        """Determine risk level based on medication count"""
        if med_count >= 10:
            return "Critical"
        elif med_count >= 7:
            return "High"
        elif med_count >= 5:
            return "Moderate"
        else:
            return "Low"

    def _generate_clinical_recommendations(
        self,
        interactions: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate clinical recommendations based on interactions"""
        recommendations = set()

        if not interactions:
            recommendations.add("Continue routine medication monitoring.")
            return list(recommendations)

        # Find max severity
        max_severity = max(
            [SEVERITY_LEVELS.get(i.get("severity", "Low"), 1) for i in interactions],
            default=1
        )

        # Get severity key from level
        severity_key = next(
            (k for k, v in SEVERITY_LEVELS.items() if v == max_severity),
            "Low"
        )

        # Add recommendations based on severity
        recommendations.update(CLINICAL_RECOMMENDATIONS.get(severity_key, []))

        # Add specific recommendations
        if len(interactions) > 2:
            recommendations.add("Multiple interactions detected. Comprehensive medication review recommended.")

        high_severity_interactions = [i for i in interactions if i.get("severity") in ["High", "Critical"]]
        if high_severity_interactions:
            recommendations.add("Consider discontinuing or replacing high-risk medications.")
            recommendations.add("Increase frequency of patient follow-up and monitoring.")

        return list(recommendations)

    def _calculate_risk_summary(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall risk summary"""
        if not interactions:
            return {
                "total_interactions": 0,
                "critical_count": 0,
                "high_count": 0,
                "moderate_count": 0,
                "low_count": 0,
                "overall_risk": "Low"
            }

        summary = {
            "total_interactions": len(interactions),
            "critical_count": len([i for i in interactions if i.get("severity") == "Critical"]),
            "high_count": len([i for i in interactions if i.get("severity") == "High"]),
            "moderate_count": len([i for i in interactions if i.get("severity") == "Moderate"]),
            "low_count": len([i for i in interactions if i.get("severity") == "Low"])
        }

        # Determine overall risk
        if summary["critical_count"] > 0:
            summary["overall_risk"] = "Critical"
        elif summary["high_count"] > 0:
            summary["overall_risk"] = "High"
        elif summary["moderate_count"] > 0:
            summary["overall_risk"] = "Moderate"
        else:
            summary["overall_risk"] = "Low"

        return summary

    def _generate_report_id(self) -> str:
        """Generate unique report ID"""
        from datetime import datetime
        return f"RPT{datetime.now().strftime('%Y%m%d%H%M%S')}"

    def _to_text_report(self, report: Dict[str, Any]) -> str:
        """Convert report to text format"""
        builder = ReportBuilder()

        # Header
        builder.add_heading("MEDICATION SAFETY REPORT - HC-03", level=1)
        builder.add_text(f"Report ID: {report['report_id']}")
        builder.add_text(f"Generated: {report['generated_at']}\n")

        # Patient Summary
        summary = report["patient_summary"]
        builder.add_section(
            "PATIENT SUMMARY",
            f"Patient ID: {summary['patient_id']}\n"
            f"Age: {summary['age']}\n"
            f"Medications: {summary['medication_count']}\n"
            f"Documented Interactions: {summary['interaction_count']}"
        )

        # Medication List
        meds = report["medication_list"]
        builder.add_section(
            "MEDICATION LIST",
            f"Total Medications: {meds['total_count']}\n" +
            "\n".join(TextFormatter.format_list_item(med) for med in meds["medications"])
        )

        # Risk Summary
        risk = report["risk_summary"]
        builder.add_section(
            "INTERACTION RISK SUMMARY",
            f"Total Interactions: {risk['total_interactions']}\n"
            f"Critical: {risk['critical_count']} {severity_to_emoji('Critical')}\n"
            f"High: {risk['high_count']} {severity_to_emoji('High')}\n"
            f"Moderate: {risk['moderate_count']} {severity_to_emoji('Moderate')}\n"
            f"Low: {risk['low_count']} {severity_to_emoji('Low')}\n"
            f"Overall Risk Level: {risk['overall_risk']}"
        )

        # Drug Interactions
        if report["interactions"]:
            interactions_text = ""
            for idx, interaction in enumerate(report["interactions"], 1):
                interactions_text += (
                    f"\n{idx}. {interaction['drug_1']} + {interaction['drug_2']}\n"
                    f"   Severity: {interaction['severity']} {interaction['severity_emoji']}\n"
                    f"   Clinical Risk: {interaction['clinical_risk']}\n"
                    f"   Explanation: {interaction['ai_explanation']}\n"
                )
            builder.add_section("DRUG INTERACTION DETAILS", interactions_text)

        # Polypharmacy Assessment
        poly = report["polypharmacy_assessment"]
        poly_status = "YES - HIGH RISK" if poly["is_polypharmacy"] else "NO"
        builder.add_section(
            "POLYPHARMACY ASSESSMENT",
            f"Polypharmacy Status: {poly_status}\n"
            f"Medications: {poly['medication_count']} (Threshold: {poly['threshold']})\n"
            f"Risk Level: {poly['risk_level']}\n\n"
            f"Assessment: {poly['warning']}"
        )

        # Clinical Recommendations
        recommendations_text = "\n".join(
            TextFormatter.format_list_item(rec)
            for rec in report["clinical_recommendations"]
        )
        builder.add_section("CLINICAL RECOMMENDATIONS", recommendations_text)

        # Footer
        builder.add_text("\n" + "=" * 80)
        builder.add_text("This report is for clinical decision support only.")
        builder.add_text("Always consult clinical pharmacist or physician.")
        builder.add_text("=" * 80)

        return builder.build()

    def _to_pdf_report(self, report: Dict[str, Any]) -> Optional[str]:
        """Convert report to PDF format"""
        try:
            text_report = self._to_text_report(report)
            pdf_filename = f"Report_{report['report_id']}.pdf"

            exporter = PDFExporter(pdf_filename)
            result = exporter.generate_pdf_from_text(
                "MEDICATION SAFETY REPORT - HC-03",
                text_report
            )

            logger.info(f"PDF report generated: {pdf_filename}")
            return result

        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            return None


if __name__ == "__main__":
    # Test Report Generator
    sample_data = {
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
    }

    generator = ReportGenerator()
    report = generator.generate_report(sample_data, output_format="json")
    print(json.dumps(report, indent=2))
