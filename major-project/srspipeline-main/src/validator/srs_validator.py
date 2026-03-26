"""SRS Validator - Validates generated SRS documents using Gemini AI."""

import os
from typing import Optional, List
from google import genai
from dotenv import load_dotenv

from src.templates import get_template

load_dotenv()


class SRSValidator:
    """SRS Document Validator using Google Gemini AI."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the SRS Validator.
        
        Args:
            api_key: Optional Gemini API key. If not provided, uses GOOGLE_GEMINI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("GOOGLE_GEMINI_API_KEY")
        self.gemini_model = os.getenv("GEMINI_MODEL")
        if not self.api_key:
            raise ValueError("Gemini API key is required. Set GOOGLE_GEMINI_API_KEY environment variable or pass api_key parameter.")
        
        self.client = genai.Client(api_key=self.api_key)
        self.model = self.gemini_model
    
    def validate(
        self, 
        srs_document: str, 
        user_requirement: str,
        template_name: str,
        validation_criteria: Optional[List[str]] = None
    ) -> dict:
        """Validate an SRS document against user requirements and template criteria.
        
        Args:
            srs_document: The generated SRS document to validate
            user_requirement: The original user requirement
            template_name: The template used for generation
            validation_criteria: Optional list of validation criteria
        
        Returns:
            dict containing:
                - is_valid: Boolean indicating if the SRS passes validation
                - score: Validation score (0-100)
                - issues: List of issues found
                - suggestions: List of improvement suggestions
                - section_analysis: Analysis of each section
        """
        # Get template validation criteria if not provided
        if not validation_criteria:
            template = get_template(template_name)
            if template:
                validation_criteria = template.get_validation_criteria()
            else:
                validation_criteria = self._get_default_criteria()
        
        # Build validation prompt
        prompt = self._build_validation_prompt(
            srs_document=srs_document,
            user_requirement=user_requirement,
            template_name=template_name,
            validation_criteria=validation_criteria
        )
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            # Parse the validation response
            validation_result = self._parse_validation_response(response.text)
            
            return {
                "success": True,
                **validation_result,
                "metadata": {
                    "model": self.model,
                    "template_validated": template_name,
                    "criteria_count": len(validation_criteria)
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "is_valid": False,
                "score": 0
            }
    
    def _build_validation_prompt(
        self, 
        srs_document: str, 
        user_requirement: str,
        template_name: str,
        validation_criteria: List[str]
    ) -> str:
        """Build the validation prompt for Gemini."""
        criteria_text = "\n".join([f"- {c}" for c in validation_criteria])
        
        return f"""You are an expert SRS (Software Requirements Specification) document reviewer and validator.

Your task is to validate the following SRS document against the original user requirement and the template criteria.

## Original User Requirement:
{user_requirement}

## Template Used: {template_name}

## Validation Criteria:
{criteria_text}

## SRS Document to Validate:
{srs_document}

---

Please analyze the SRS document and provide a detailed validation report in the following JSON format:

```json
{{
    "is_valid": true/false,
    "score": 0-100,
    "overall_assessment": "Brief overall assessment",
    "issues": [
        {{
            "severity": "critical/major/minor",
            "category": "category name",
            "description": "Issue description",
            "location": "Where in the document"
        }}
    ],
    "suggestions": [
        {{
            "category": "category name",
            "suggestion": "Improvement suggestion",
            "priority": "high/medium/low"
        }}
    ],
    "section_analysis": [
        {{
            "section_name": "Section name",
            "present": true/false,
            "quality": "excellent/good/fair/poor/missing",
            "notes": "Analysis notes"
        }}
    ],
    "requirement_coverage": {{
        "covered_requirements": ["list of covered requirements from user input"],
        "missing_requirements": ["list of requirements not adequately covered"],
        "coverage_percentage": 0-100
    }},
    "criteria_checklist": [
        {{
            "criterion": "The validation criterion",
            "passed": true/false,
            "notes": "Notes on this criterion"
        }}
    ]
}}
```

Be thorough but fair in your assessment. Focus on:
1. Does the SRS accurately reflect the user's requirements?
2. Are all required sections present and complete?
3. Is the document well-structured and professional?
4. Are functional requirements properly numbered and traceable?
5. Are non-functional requirements specific and measurable?
6. Is the document suitable for actual software development?

Provide only the JSON response, no additional text."""

    def _parse_validation_response(self, response_text: str) -> dict:
        """Parse the validation response from Gemini."""
        import json
        import re
        
        # Try to extract JSON from the response
        try:
            # Look for JSON block in markdown code blocks
            json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1).strip()
            else:
                # Try to parse the entire response as JSON
                json_str = response_text.strip()
            
            result = json.loads(json_str)
            return result
        except json.JSONDecodeError:
            # If JSON parsing fails, return a basic structure
            return {
                "is_valid": False,
                "score": 0,
                "overall_assessment": "Failed to parse validation response",
                "issues": [{"severity": "critical", "category": "parsing", "description": "Could not parse validation response"}],
                "suggestions": [],
                "section_analysis": [],
                "raw_response": response_text
            }
    
    def _get_default_criteria(self) -> List[str]:
        """Get default validation criteria."""
        return [
            "Document must have clear introduction and purpose",
            "Functional requirements must be present and numbered",
            "Non-functional requirements must be specified",
            "Document must be relevant to user requirements",
            "Document must be well-structured and readable",
            "All major sections must be present"
        ]
    
    def quick_validate(self, srs_document: str, user_requirement: str) -> dict:
        """Perform a quick validation check.
        
        Args:
            srs_document: The generated SRS document
            user_requirement: The original user requirement
        
        Returns:
            dict with basic validation results
        """
        prompt = f"""You are an SRS document validator. Quickly assess if this SRS document adequately addresses the user requirement.

User Requirement: {user_requirement}

SRS Document (first 2000 chars): {srs_document[:2000]}

Respond with JSON:
{{
    "is_adequate": true/false,
    "confidence": 0-100,
    "brief_assessment": "One sentence assessment",
    "key_issues": ["issue1", "issue2"] (max 3 issues, empty if none)
}}

Only respond with JSON, no other text."""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            return self._parse_validation_response(response.text)
        except Exception as e:
            return {
                "is_adequate": False,
                "confidence": 0,
                "brief_assessment": f"Validation failed: {str(e)}",
                "key_issues": ["Validation error"]
            }
