"""SRS Generator - Generates SRS documents using Gemini AI."""

import os
import logging
from typing import Optional
from google import genai
from google.genai.errors import ClientError
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.templates import TemplateRegistry, get_template

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


class SRSGenerator:
    """SRS Document Generator using Google Gemini AI."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the SRS Generator.
        
        Args:
            api_key: Optional Gemini API key. If not provided, uses GOOGLE_GEMINI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("GOOGLE_GEMINI_API_KEY")
        # Set default model if not specified
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        
        if not self.api_key:
            logger.error("Gemini API key is missing")
            raise ValueError("Gemini API key is required. Set GOOGLE_GEMINI_API_KEY environment variable or pass api_key parameter.")
        
        logger.info(f"Initializing SRSGenerator with model: {self.gemini_model}")
        try:
            self.client = genai.Client(api_key=self.api_key)
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            raise
        
        self.model = self.gemini_model

    @retry(
        retry=retry_if_exception_type(ClientError),
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        reraise=True
    )
    def _generate_with_retry(self, prompt: str):
        """Internal method to call Gemini API with retry logic."""
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )
        return response
    
    def generate(
        self, 
        user_requirement: str, 
        template_name: Optional[str] = None,
        custom_instructions: Optional[str] = None
    ) -> dict:
        """Generate an SRS document based on user requirements.
        
        Args:
            user_requirement: The user's project/product requirements
            template_name: Optional template name (agile, ieee, minimal, startup)
                          If not provided, auto-detects based on requirement content
            custom_instructions: Optional additional instructions for generation
        
        Returns:
            dict containing:
                - srs_document: The generated SRS in Markdown format
                - template_used: The template that was used
                - metadata: Additional metadata about the generation
        """
        try:
            # Auto-detect or use provided template
            if template_name:
                selected_template = template_name.lower()
            else:
                selected_template = TemplateRegistry.get_template_for_requirement(user_requirement)
            
            # Get the template
            template = get_template(selected_template)
            if not template:
                # Fallback to agile if template not found
                logger.warning(f"Template '{selected_template}' not found, falling back to 'agile'")
                template = get_template("agile")
                selected_template = "agile"
            
            logger.info(f"Using template: {selected_template}")
            
            # Build the prompt
            prompt = template.get_prompt_template().format(user_requirement=user_requirement)
            
            # Add custom instructions if provided
            if custom_instructions:
                prompt += f"\n\n**Additional Instructions:**\n{custom_instructions}"
            
            logger.info("Sending request to Gemini API...")
            
            # Generate using Gemini with retry
            try:
                response = self._generate_with_retry(prompt)
            except Exception as retry_err:
                 # Check if it was specifically a 429 that exhausted retries
                 if "429" in str(retry_err) or "RESOURCE_EXHAUSTED" in str(retry_err):
                     logger.error("Quota exceeded even after retries.")
                     raise ValueError("Gemini API Quota Exceeded. Please try again later or check billing.") from retry_err
                 raise retry_err

            if not response.text:
                raise ValueError("Gemini returned empty response")
                
            srs_document = response.text
            logger.info("Successfully generated SRS document")
            
            return {
                "success": True,
                "srs_document": srs_document,
                "template_used": selected_template,
                "template_description": template.description,
                "sections": template.sections,
                "validation_criteria": template.get_validation_criteria(),
                "metadata": {
                    "model": self.model,
                    "user_requirement_length": len(user_requirement),
                    "output_length": len(srs_document)
                }
            }
        except Exception as e:
            logger.error(f"SRS Generation failed: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "template_used": selected_template if 'selected_template' in locals() else None,
                "srs_document": None
            }
    
    def list_available_templates(self) -> list:
        """List all available SRS templates."""
        return TemplateRegistry.list_templates()
    
    def get_template_info(self, template_name: str) -> Optional[dict]:
        """Get information about a specific template."""
        template = get_template(template_name)
        if template:
            return {
                "name": template.name,
                "description": template.description,
                "sections": template.get_sections(),
                "validation_criteria": template.get_validation_criteria()
            }
        return None
