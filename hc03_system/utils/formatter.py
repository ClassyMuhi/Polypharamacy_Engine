"""
Formatter Utility Module
Handles text and data formatting for reports
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class TextFormatter:
    """Formats text data for reports"""

    @staticmethod
    def format_heading(text: str, level: int = 1) -> str:
        """
        Format text as heading
        Args:
            text: Heading text
            level: Heading level (1-3)
        Returns:
            Formatted heading string
        """
        if level == 1:
            return f"\n{'=' * 80}\n{text}\n{'=' * 80}\n"
        elif level == 2:
            return f"\n{'-' * 60}\n{text}\n{'-' * 60}\n"
        else:
            return f"\n{text}\n{'-' * 40}\n"

    @staticmethod
    def format_section(title: str, content: str) -> str:
        """Format a section with title and content"""
        return f"\n{title}\n{'-' * len(title)}\n{content}\n"

    @staticmethod
    def format_list_item(item: str, level: int = 0) -> str:
        """
        Format text as list item
        Args:
            item: Item text
            level: Indentation level
        Returns:
            Formatted list item
        """
        indent = "  " * level
        return f"{indent}• {item}\n"

    @staticmethod
    def format_severity_badge(severity: str) -> str:
        """Format severity as badge-like text"""
        severity = severity.upper()
        length = len(severity) + 4
        border = "-" * length
        return f"\n {border}\n | {severity} |\n {border}\n"


class DataFormatter:
    """Formats structured data for reports"""

    @staticmethod
    def format_medication_list(medications: List[str]) -> str:
        """Format medication list"""
        formatted = ""
        for med in medications:
            formatted += TextFormatter.format_list_item(med)
        return formatted

    @staticmethod
    def format_interaction(interaction: Dict[str, Any]) -> str:
        """
        Format single interaction for display
        Args:
            interaction: Interaction dictionary
        Returns:
            Formatted interaction string
        """
        formatted = f"""
  Drug 1: {interaction.get('drug_1', 'N/A')}
  Drug 2: {interaction.get('drug_2', 'N/A')}
  Severity: {interaction.get('severity', 'N/A')}
  Clinical Risk: {interaction.get('clinical_risk', 'N/A')}
        """.strip()
        return formatted

    @staticmethod
    def format_interactions_list(interactions: List[Dict[str, Any]]) -> str:
        """Format multiple interactions with numbering"""
        formatted = ""
        for idx, interaction in enumerate(interactions, 1):
            formatted += f"\n{idx}. {DataFormatter.format_interaction(interaction)}\n"
        return formatted

    @staticmethod
    def format_json(data: Dict[str, Any], indent: int = 2) -> str:
        """Format data as JSON string"""
        return json.dumps(data, indent=indent)

    @staticmethod
    def format_timestamp() -> str:
        """Get formatted current timestamp"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class ReportBuilder:
    """Builds complete reports from components"""

    def __init__(self):
        self.sections: List[str] = []

    def add_heading(self, text: str, level: int = 1) -> "ReportBuilder":
        """Add heading section"""
        self.sections.append(TextFormatter.format_heading(text, level))
        return self

    def add_section(self, title: str, content: str) -> "ReportBuilder":
        """Add titled section"""
        self.sections.append(TextFormatter.format_section(title, content))
        return self

    def add_text(self, text: str) -> "ReportBuilder":
        """Add plain text"""
        self.sections.append(text + "\n")
        return self

    def build(self) -> str:
        """Build final report"""
        return "".join(self.sections)


def severity_to_emoji(severity: str) -> str:
    """Convert severity level to emoji"""
    severity_map = {
        "Critical": "🔴",
        "High": "🟠",
        "Moderate": "🟡",
        "Low": "🟢"
    }
    return severity_map.get(severity, "⚪")


if __name__ == "__main__":
    # Test formatter
    fmt = TextFormatter()
    print(fmt.format_heading("Test Heading"))
    print(fmt.format_list_item("Test Item"))
    print(fmt.format_severity_badge("High"))
