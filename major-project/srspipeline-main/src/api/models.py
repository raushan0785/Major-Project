"""API Models - Pydantic models for API requests and responses."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class TemplateType(str, Enum):
    """Available SRS template types."""
    AGILE = "agile"
    IEEE = "ieee"
    MINIMAL = "minimal"
    STARTUP = "startup"


# Request Models

class GenerateSRSRequest(BaseModel):
    """Request model for SRS generation."""
    user_requirement: str = Field(
        ...,
        description="The user's project/product requirements",
        min_length=10,
        examples=["I want to build an e-commerce platform for selling handmade crafts"]
    )
    template_name: Optional[TemplateType] = Field(
        None,
        description="The SRS template to use. If not provided, auto-detected based on requirement content"
    )
    custom_instructions: Optional[str] = Field(
        None,
        description="Optional additional instructions for the generation"
    )
    validate: bool = Field(
        True,
        description="Whether to validate the generated SRS"
    )
    auto_fix: bool = Field(
        False,
        description="Whether to automatically attempt to fix validation issues"
    )
    max_retries: int = Field(
        2,
        description="Maximum retries for auto-fix (only used if auto_fix is True)",
        ge=0,
        le=5
    )


class QuickGenerateRequest(BaseModel):
    """Request model for quick SRS generation without validation."""
    user_requirement: str = Field(
        ...,
        description="The user's project/product requirements",
        min_length=10
    )
    template_name: Optional[TemplateType] = Field(
        None,
        description="The SRS template to use"
    )


class ValidateSRSRequest(BaseModel):
    """Request model for SRS validation."""
    srs_document: str = Field(
        ...,
        description="The SRS document to validate",
        min_length=100
    )
    user_requirement: str = Field(
        ...,
        description="The original user requirement",
        min_length=10
    )
    template_name: TemplateType = Field(
        ...,
        description="The template used for the SRS"
    )


class SuggestTemplateRequest(BaseModel):
    """Request model for template suggestion."""
    user_requirement: str = Field(
        ...,
        description="The user's requirement text",
        min_length=10
    )


# Response Models

class ValidationIssue(BaseModel):
    """A validation issue found in the SRS."""
    severity: str = Field(..., description="Issue severity: critical, major, or minor")
    category: str = Field(..., description="Issue category")
    description: str = Field(..., description="Issue description")
    location: Optional[str] = Field(None, description="Location in the document")


class ValidationSuggestion(BaseModel):
    """A suggestion for improving the SRS."""
    category: str = Field(..., description="Suggestion category")
    suggestion: str = Field(..., description="The improvement suggestion")
    priority: str = Field(..., description="Priority: high, medium, or low")


class SectionAnalysis(BaseModel):
    """Analysis of a single section."""
    section_name: str = Field(..., description="Name of the section")
    present: bool = Field(..., description="Whether the section is present")
    quality: str = Field(..., description="Quality rating")
    notes: Optional[str] = Field(None, description="Analysis notes")


class RequirementCoverage(BaseModel):
    """Coverage analysis of user requirements."""
    covered_requirements: List[str] = Field(default_factory=list)
    missing_requirements: List[str] = Field(default_factory=list)
    coverage_percentage: float = Field(0, ge=0, le=100)


class ValidationResult(BaseModel):
    """Complete validation result."""
    success: bool = Field(..., description="Whether validation completed successfully")
    is_valid: bool = Field(False, description="Whether the SRS passes validation")
    score: float = Field(0, description="Validation score (0-100)", ge=0, le=100)
    overall_assessment: Optional[str] = Field(None, description="Overall assessment")
    issues: List[ValidationIssue] = Field(default_factory=list)
    suggestions: List[ValidationSuggestion] = Field(default_factory=list)
    section_analysis: List[SectionAnalysis] = Field(default_factory=list)
    requirement_coverage: Optional[RequirementCoverage] = None
    error: Optional[str] = Field(None, description="Error message if validation failed")


class GenerateSRSResponse(BaseModel):
    """Response model for SRS generation."""
    success: bool = Field(..., description="Whether generation was successful")
    user_requirement: str = Field(..., description="The original user requirement")
    template_used: Optional[str] = Field(None, description="The template that was used")
    template_description: Optional[str] = Field(None, description="Description of the template")
    sections: Optional[List[str]] = Field(None, description="Sections in the generated SRS")
    srs_document: Optional[str] = Field(None, description="The generated SRS document in Markdown format")
    validation_result: Optional[Dict[str, Any]] = Field(None, description="Validation results if validation was performed")
    iterations: int = Field(0, description="Number of generation iterations")
    final_score: float = Field(0, description="Final validation score", ge=0, le=100)
    error: Optional[str] = Field(None, description="Error message if generation failed")


class ValidateSRSResponse(BaseModel):
    """Response model for SRS validation."""
    success: bool = Field(..., description="Whether validation completed successfully")
    is_valid: bool = Field(False, description="Whether the SRS passes validation")
    score: float = Field(0, description="Validation score (0-100)")
    overall_assessment: Optional[str] = None
    issues: List[Dict[str, Any]] = Field(default_factory=list)
    suggestions: List[Dict[str, Any]] = Field(default_factory=list)
    section_analysis: List[Dict[str, Any]] = Field(default_factory=list)
    requirement_coverage: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class SectionInfo(BaseModel):
    """Information about a template section."""
    name: str
    description: str


class TemplateInfo(BaseModel):
    """Information about an SRS template."""
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    sections: List[str] = Field(..., description="List of section names")


class TemplateDetailInfo(BaseModel):
    """Detailed information about an SRS template."""
    name: str
    description: str
    sections: List[SectionInfo]
    validation_criteria: List[str]


class TemplateListResponse(BaseModel):
    """Response model for listing templates."""
    templates: List[TemplateInfo]
    count: int


class TemplateSuggestionResponse(BaseModel):
    """Response model for template suggestion."""
    suggested_template: str = Field(..., description="The suggested template name")
    template_info: Optional[TemplateDetailInfo] = None
    all_templates: List[TemplateInfo] = Field(default_factory=list)


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field("ok", description="Service status")
    service: str = Field("srs-pipeline", description="Service name")
    version: str = Field("1.0.0", description="Service version")
