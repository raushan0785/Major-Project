import os
from typing import Optional, List
from dotenv import load_dotenv

from src.generator import SRSGenerator
from src.validator import SRSValidator
from src.templates import TemplateRegistry, list_templates

load_dotenv()


class SRSPipeline:
    """Complete SRS generation pipeline with validation."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the SRS Pipeline.
        
        Args:
            api_key: Optional Gemini API key. If not provided, uses GOOGLE_GEMINI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("GOOGLE_GEMINI_API_KEY")
        self.gemini_model = os.getenv("GEMINI_MODEL")
        self.generator = SRSGenerator(api_key=self.api_key)
        self.validator = SRSValidator(api_key=self.api_key)
    
    def run(
        self,
        user_requirement: str,
        template_name: Optional[str] = None,
        custom_instructions: Optional[str] = None,
        validate: bool = True,
        auto_fix: bool = False,
        max_retries: int = 2
    ) -> dict:
        """Run the complete SRS generation pipeline.
        
        Args:
            user_requirement: The user's project/product requirements
            template_name: Optional template name (agile, ieee, minimal, startup)
            custom_instructions: Optional additional instructions
            validate: Whether to validate the generated SRS
            auto_fix: Whether to automatically attempt to fix validation issues
            max_retries: Maximum retries for auto-fix
        
        Returns:
            dict containing the complete pipeline result
        """
        result = {
            "success": False,
            "user_requirement": user_requirement,
            "template_used": None,
            "srs_document": None,
            "validation_result": None,
            "iterations": 0,
            "final_score": 0
        }
        
        # Step 1: Generate the SRS
        generation_result = self.generator.generate(
            user_requirement=user_requirement,
            template_name=template_name,
            custom_instructions=custom_instructions
        )
        
        if not generation_result.get("success"):
            result["error"] = generation_result.get("error", "Generation failed")
            return result
        
        result["srs_document"] = generation_result["srs_document"]
        result["template_used"] = generation_result["template_used"]
        result["template_description"] = generation_result.get("template_description")
        result["sections"] = generation_result.get("sections")
        result["iterations"] = 1
        
        # Step 2: Validate if requested
        if validate:
            validation_result = self.validator.validate(
                srs_document=result["srs_document"],
                user_requirement=user_requirement,
                template_name=result["template_used"],
                validation_criteria=generation_result.get("validation_criteria")
            )
            
            result["validation_result"] = validation_result
            result["final_score"] = validation_result.get("score", 0)
            
            # Step 3: Auto-fix if enabled and validation found issues
            if auto_fix and not validation_result.get("is_valid", False):
                result = self._attempt_auto_fix(
                    result=result,
                    user_requirement=user_requirement,
                    validation_result=validation_result,
                    max_retries=max_retries
                )
        
        result["success"] = True
        return result
    
    def _attempt_auto_fix(
        self,
        result: dict,
        user_requirement: str,
        validation_result: dict,
        max_retries: int
    ) -> dict:
        """Attempt to fix validation issues by regenerating with feedback.
        
        Args:
            result: Current pipeline result
            user_requirement: Original user requirement
            validation_result: Validation result with issues
            max_retries: Maximum number of retry attempts
        
        Returns:
            Updated result dict
        """
        for attempt in range(max_retries):
            # Build fix instructions from validation issues
            issues = validation_result.get("issues", [])
            suggestions = validation_result.get("suggestions", [])
            
            fix_instructions = self._build_fix_instructions(issues, suggestions)
            
            if not fix_instructions:
                break
            
            # Regenerate with fix instructions
            regeneration_result = self.generator.generate(
                user_requirement=user_requirement,
                template_name=result["template_used"],
                custom_instructions=f"Previous version had these issues that need to be fixed:\n{fix_instructions}"
            )
            
            if not regeneration_result.get("success"):
                break
            
            result["srs_document"] = regeneration_result["srs_document"]
            result["iterations"] += 1
            
            # Re-validate
            validation_result = self.validator.validate(
                srs_document=result["srs_document"],
                user_requirement=user_requirement,
                template_name=result["template_used"]
            )
            
            result["validation_result"] = validation_result
            result["final_score"] = validation_result.get("score", 0)
            
            # Stop if validation passes
            if validation_result.get("is_valid", False):
                break
        
        return result
    
    def _build_fix_instructions(self, issues: List[dict], suggestions: List[dict]) -> str:
        """Build fix instructions from validation issues and suggestions."""
        instructions = []
        
        # Add critical and major issues
        for issue in issues:
            if issue.get("severity") in ["critical", "major"]:
                instructions.append(f"- FIX: {issue.get('description', 'Unknown issue')}")
        
        # Add high priority suggestions
        for suggestion in suggestions[:3]:  # Limit to top 3 suggestions
            if suggestion.get("priority") == "high":
                instructions.append(f"- IMPROVE: {suggestion.get('suggestion', '')}")
        
        return "\n".join(instructions)
    
    def list_templates(self) -> list:
        """List all available SRS templates."""
        return list_templates()
    
    def suggest_template(self, user_requirement: str) -> dict:
        """Suggest a template based on user requirement.
        
        Args:
            user_requirement: The user's requirement text
        
        Returns:
            dict with suggested template and reasoning
        """
        suggested = TemplateRegistry.get_template_for_requirement(user_requirement)
        template_info = self.generator.get_template_info(suggested)
        
        return {
            "suggested_template": suggested,
            "template_info": template_info,
            "all_templates": self.list_templates()
        }
    
    def quick_generate(self, user_requirement: str) -> dict:
        """Quick generation without validation for fast results.
        
        Args:
            user_requirement: The user's requirement text
        
        Returns:
            Generated SRS document
        """
        return self.run(
            user_requirement=user_requirement,
            validate=False
        )
