"""
PDF Exporter Utility Module
Handles PDF report generation
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logger.warning("reportlab not available. PDF export will be limited.")


class PDFExporter:
    """Generates PDF reports using reportlab"""

    def __init__(self, filename: str = "medication_report.pdf"):
        """
        Initialize PDF exporter
        Args:
            filename: Output PDF filename
        """
        self.filename = filename
        self.styles = getSampleStyleSheet() if REPORTLAB_AVAILABLE else None

    def generate_pdf(self, title: str, content_dict: Dict[str, Any]) -> Optional[str]:
        """
        Generate PDF from content dictionary
        Args:
            title: Report title
            content_dict: Dictionary with report sections
        Returns:
            Path to generated PDF or None if reportlab unavailable
        """
        if not REPORTLAB_AVAILABLE:
            logger.error("reportlab is required for PDF export")
            return None

        try:
            # Create PDF document
            doc = SimpleDocTemplate(self.filename, pagesize=letter)
            elements = []

            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#2C3E50'),
                spaceAfter=30,
                alignment=1  # Center
            )
            elements.append(Paragraph(title, title_style))
            elements.append(Spacer(1, 0.3 * inch))

            # Add timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            elements.append(Paragraph(f"Generated: {timestamp}", self.styles['Normal']))
            elements.append(Spacer(1, 0.2 * inch))

            # Process content sections
            for section_title, section_content in content_dict.items():
                # Section heading
                heading_style = ParagraphStyle(
                    'SectionHeading',
                    parent=self.styles['Heading2'],
                    fontSize=14,
                    textColor=colors.HexColor('#34495E'),
                    spaceAfter=12,
                    spaceBefore=12
                )
                elements.append(Paragraph(section_title, heading_style))

                # Section content
                if isinstance(section_content, list):
                    for item in section_content:
                        elements.append(Paragraph(f"• {str(item)}", self.styles['Normal']))
                elif isinstance(section_content, dict):
                    for key, value in section_content.items():
                        elements.append(Paragraph(f"<b>{key}:</b> {str(value)}", self.styles['Normal']))
                else:
                    elements.append(Paragraph(str(section_content), self.styles['Normal']))

                elements.append(Spacer(1, 0.2 * inch))

            # Build PDF
            doc.build(elements)
            logger.info(f"PDF generated: {self.filename}")
            return self.filename

        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            return None

    def generate_pdf_from_text(self, title: str, text_content: str) -> Optional[str]:
        """
        Generate PDF from plain text
        Args:
            title: Report title
            text_content: Plain text content
        Returns:
            Path to generated PDF or None
        """
        if not REPORTLAB_AVAILABLE:
            logger.error("reportlab is required for PDF export")
            return None

        try:
            doc = SimpleDocTemplate(self.filename, pagesize=letter)
            elements = []

            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=20,
                textColor=colors.HexColor('#2C3E50'),
                spaceAfter=20,
                alignment=1
            )
            elements.append(Paragraph(title, title_style))
            elements.append(Spacer(1, 0.2 * inch))

            # Convert text to paragraphs
            paragraphs = text_content.split('\n')
            for para in paragraphs:
                if para.strip():
                    if para.startswith('===') or para.startswith('---'):
                        continue
                    elements.append(Paragraph(para, self.styles['Normal']))
                elements.append(Spacer(1, 0.1 * inch))

            # Build PDF
            doc.build(elements)
            logger.info(f"PDF generated from text: {self.filename}")
            return self.filename

        except Exception as e:
            logger.error(f"Error generating PDF from text: {str(e)}")
            return None


def export_report_to_pdf(
    report_text: str,
    title: str = "Medication Safety Report",
    output_file: str = "report.pdf"
) -> Optional[str]:
    """
    Convenience function to export report to PDF
    Args:
        report_text: Report text content
        title: Report title
        output_file: Output file path
    Returns:
        Path to generated PDF or None
    """
    exporter = PDFExporter(output_file)
    return exporter.generate_pdf_from_text(title, report_text)


if __name__ == "__main__":
    # Test PDF export
    if REPORTLAB_AVAILABLE:
        test_content = {
            "Patient Info": {"ID": "P001", "Age": 72},
            "Medications": ["Warfarin", "Aspirin"],
            "Warnings": ["High risk interaction detected"]
        }
        exporter = PDFExporter("test_report.pdf")
        result = exporter.generate_pdf("Test Report", test_content)
        if result:
            print(f"PDF generated: {result}")
    else:
        print("reportlab not available")
