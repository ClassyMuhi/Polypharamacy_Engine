"""
AI Explanation Engine Module
Generates clear explanations for drug interactions using LLM
"""

import logging
from typing import Dict, Any, Optional
import os

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI, APIError
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not available. AI explanations will use fallback mode.")


class AIExplanationEngine:
    """Generates AI-powered explanations for drug interactions"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize AI Engine
        Args:
            api_key: OpenAI API key (if None, uses environment variable)
            model: LLM model to use
        """
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if OPENAI_AVAILABLE and self.api_key and self.api_key != "your-api-key-here":
            try:
                self.client = OpenAI(api_key=self.api_key)
                self.available = True
                logger.info(f"AI Engine initialized with model: {model}")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {str(e)}")
                self.available = False
        else:
            self.available = False
            if not OPENAI_AVAILABLE:
                logger.warning("OpenAI library not installed")
            elif not self.api_key or self.api_key == "your-api-key-here":
                logger.warning("No valid OpenAI API key provided")

    def generate_explanation(
        self,
        drug_1: str,
        drug_2: str,
        severity: str,
        clinical_risk: str
    ) -> str:
        """
        Generate AI explanation for drug interaction
        Args:
            drug_1: First drug name
            drug_2: Second drug name
            severity: Severity level (Low/Moderate/High/Critical)
            clinical_risk: Clinical risk description
        Returns:
            Explanation text
        """
        if self.available:
            try:
                return self._generate_with_llm(drug_1, drug_2, severity, clinical_risk)
            except Exception as e:
                logger.error(f"LLM error: {str(e)}. Using fallback.")
                return self._generate_fallback(drug_1, drug_2, severity, clinical_risk)
        else:
            return self._generate_fallback(drug_1, drug_2, severity, clinical_risk)

    def _generate_with_llm(
        self,
        drug_1: str,
        drug_2: str,
        severity: str,
        clinical_risk: str
    ) -> str:
        """Generate explanation using OpenAI API"""
        prompt = f"""You are a clinical pharmacology assistant. Explain the following drug interaction clearly for doctors treating elderly patients (72+ years). 

Drug Interaction:
- Drug 1: {drug_1}
- Drug 2: {drug_2}
- Severity: {severity}
- Clinical Risk: {clinical_risk}

Provide a concise explanation (2-3 sentences) covering:
1. Why this interaction occurs
2. Specific risk for elderly patients
3. Recommended clinical action

Keep language clear but professional for healthcare practitioners."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a clinical pharmacology expert"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            explanation = response.choices[0].message.content.strip()
            logger.info(f"Generated explanation for {drug_1} + {drug_2}")
            return explanation

        except APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise

    def _generate_fallback(
        self,
        drug_1: str,
        drug_2: str,
        severity: str,
        clinical_risk: str
    ) -> str:
        """Generate explanation using predefined templates (fallback)"""
        
        severity_text = {
            "Critical": "This is a critical interaction that requires immediate clinical attention",
            "High": "This is a significant interaction requiring careful monitoring",
            "Moderate": "This interaction requires attention and possible medication adjustment",
            "Low": "This is a minor interaction that should be documented"
        }
        
        base_explanation = f"{drug_1} and {drug_2} interact due to: {clinical_risk}. "
        
        if severity == "Critical":
            explanation = base_explanation + (
                f"In elderly patients, this combination significantly increases adverse event risk. "
                f"Consider discontinuing one medication or selecting alternatives. "
                f"Close monitoring is essential."
            )
        elif severity == "High":
            explanation = base_explanation + (
                f"Elderly patients are at elevated risk. "
                f"Review medication necessity and timing. "
                f"Implement regular monitoring for adverse effects."
            )
        elif severity == "Moderate":
            explanation = base_explanation + (
                f"Monitor patient for signs of adverse effects. "
                f"Consider adjusting dosages or timing. "
                f"Patient should be informed of potential risks."
            )
        else:  # Low
            explanation = base_explanation + (
                f"Document this interaction in the patient record. "
                f"Continue routine monitoring during treatment."
            )
        
        logger.info(f"Generated fallback explanation for {drug_1} + {drug_2}")
        return explanation

    def generate_polypharmacy_warning(self, medication_count: int) -> str:
        """
        Generate warning for polypharmacy
        Args:
            medication_count: Number of medications
        Returns:
            Warning text
        """
        if self.available:
            try:
                return self._generate_polypharmacy_llm(medication_count)
            except Exception as e:
                logger.error(f"LLM error for polypharmacy: {str(e)}")
                return self._generate_polypharmacy_fallback(medication_count)
        else:
            return self._generate_polypharmacy_fallback(medication_count)

    def _generate_polypharmacy_llm(self, medication_count: int) -> str:
        """Generate polypharmacy warning using LLM"""
        prompt = f"""You are a clinical pharmacology assistant. Generate a brief warning about polypharmacy (multiple medication use) for an elderly patient taking {medication_count} medications.

Provide key concerns:
1. Main risks of multiple medications in elderly
2. Need for medication review
3. Recommended clinical actions

Keep it to 3-4 sentences, professional tone for doctors."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a clinical pharmacology expert"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            warning = response.choices[0].message.content.strip()
            logger.info(f"Generated polypharmacy warning for {medication_count} medications")
            return warning

        except APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise

    def _generate_polypharmacy_fallback(self, medication_count: int) -> str:
        """Generate polypharmacy warning using template (fallback)"""
        
        if medication_count >= 10:
            return (
                f"CRITICAL: Patient is taking {medication_count} medications (severe polypharmacy). "
                f"This significantly increases risks of adverse drug events, drug-drug interactions, "
                f"and medication errors in elderly patients. "
                f"Immediate comprehensive medication review is STRONGLY RECOMMENDED. "
                f"Consider deprescribing clinically unnecessary medications."
            )
        elif medication_count >= 7:
            return (
                f"HIGH RISK: Patient is taking {medication_count} medications (moderate-to-high polypharmacy). "
                f"Elderly patients are at increased risk for adverse effects and interactions. "
                f"Conduct a thorough medication review to identify and eliminate unnecessary drugs. "
                f"Monitor closely for drug-related problems."
            )
        elif medication_count >= 5:
            return (
                f"ALERT: Patient meets criteria for polypharmacy with {medication_count} medications. "
                f"In elderly patients, this increases adverse event risk. "
                f"Review each medication for continued necessity and appropriateness. "
                f"Implement regular monitoring."
            )
        else:
            return (
                f"Patient is taking {medication_count} medications. "
                f"While below polypharmacy threshold, appropriate medication review is still recommended. "
                f"Ensure all medications are necessary and appropriate for elderly patients."
            )


class ExplanationCache:
    """Simple cache for explanations to reduce API calls"""

    def __init__(self):
        self.cache: Dict[str, str] = {}

    def get_key(self, drug_1: str, drug_2: str, severity: str) -> str:
        """Generate cache key"""
        return f"{drug_1.lower()}_{drug_2.lower()}_{severity.lower()}"

    def get(self, drug_1: str, drug_2: str, severity: str) -> Optional[str]:
        """Get cached explanation"""
        key = self.get_key(drug_1, drug_2, severity)
        return self.cache.get(key)

    def set(self, drug_1: str, drug_2: str, severity: str, explanation: str) -> None:
        """Cache explanation"""
        key = self.get_key(drug_1, drug_2, severity)
        self.cache[key] = explanation

    def clear(self) -> None:
        """Clear cache"""
        self.cache.clear()


# Global cache instance
explanation_cache = ExplanationCache()


if __name__ == "__main__":
    # Test AI Engine
    engine = AIExplanationEngine()
    
    # Test interaction explanation
    explanation = engine.generate_explanation(
        "Warfarin",
        "Aspirin",
        "High",
        "Increased bleeding risk"
    )
    print("Explanation:", explanation)
    
    # Test polypharmacy warning
    warning = engine.generate_polypharmacy_warning(7)
    print("\nPolypharmacy Warning:", warning)
