"""API Routes - FastAPI route definitions for SRS pipeline."""

from fastapi import APIRouter, HTTPException, status
from typing import Optional

from src.pipeline import SRSPipeline
from src.templates import list_templates, get_template
from .models import (
    GenerateSRSRequest,
    GenerateSRSResponse,
    QuickGenerateRequest,
    ValidateSRSRequest,
    ValidateSRSResponse,
    SuggestTemplateRequest,
    TemplateListResponse,
    TemplateInfo,
    TemplateDetailInfo,
    TemplateSuggestionResponse,
    SectionInfo,
    HealthResponse
)

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health check endpoint",
    description="Check if the SRS Pipeline service is running"
)
async def health_check():
    """Check service health."""
    return HealthResponse(
        status="ok",
        service="srs-pipeline",
        version="1.0.0"
    )


@router.get(
    "/templates",
    response_model=TemplateListResponse,
    tags=["Templates"],
    summary="List available templates",
    description="Get a list of all available SRS templates with their descriptions and sections"
)
async def get_templates():
    """List all available SRS templates."""
    templates = list_templates()
    template_list = [
        TemplateInfo(
            name=t["name"],
            description=t["description"],
            sections=t["sections"]
        )
        for t in templates
    ]
    return TemplateListResponse(
        templates=template_list,
        count=len(template_list)
    )


@router.get(
    "/templates/{template_name}",
    response_model=TemplateDetailInfo,
    tags=["Templates"],
    summary="Get template details",
    description="Get detailed information about a specific SRS template including validation criteria"
)
async def get_template_details(template_name: str):
    """Get detailed information about a specific template."""
    template = get_template(template_name)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template '{template_name}' not found. Available templates: agile, ieee, minimal, startup"
        )
    
    sections = [
        SectionInfo(name=s["name"], description=s["description"])
        for s in template.get_sections()
    ]
    
    return TemplateDetailInfo(
        name=template.name,
        description=template.description,
        sections=sections,
        validation_criteria=template.get_validation_criteria()
    )


@router.post(
    "/templates/suggest",
    response_model=TemplateSuggestionResponse,
    tags=["Templates"],
    summary="Suggest template for requirement",
    description="Analyze user requirement and suggest the most appropriate SRS template"
)
async def suggest_template(request: SuggestTemplateRequest):
    """Suggest a template based on user requirement."""
    try:
        pipeline = SRSPipeline()
        result = pipeline.suggest_template(request.user_requirement)
        
        # Convert template_info to proper format
        template_info = None
        if result.get("template_info"):
            ti = result["template_info"]
            template_info = TemplateDetailInfo(
                name=ti["name"],
                description=ti["description"],
                sections=[SectionInfo(name=s["name"], description=s["description"]) for s in ti["sections"]],
                validation_criteria=ti["validation_criteria"]
            )
        
        all_templates = [
            TemplateInfo(name=t["name"], description=t["description"], sections=t["sections"])
            for t in result.get("all_templates", [])
        ]
        
        return TemplateSuggestionResponse(
            suggested_template=result["suggested_template"],
            template_info=template_info,
            all_templates=all_templates
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/generate",
    response_model=GenerateSRSResponse,
    tags=["Generation"],
    summary="Generate SRS document",
    description="Generate a complete SRS document from user requirements with optional validation and auto-fix"
)
async def generate_srs(request: GenerateSRSRequest):
    """Generate an SRS document from user requirements."""
    try:
        pipeline = SRSPipeline()
        
        # Convert enum to string if provided
        template_name = request.template_name.value if request.template_name else None
        
        result = pipeline.run(
            user_requirement=request.user_requirement,
            template_name=template_name,
            custom_instructions=request.custom_instructions,
            validate=request.validate,
            auto_fix=request.auto_fix,
            max_retries=request.max_retries
        )
        
        return GenerateSRSResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Generation failed: {str(e)}"
        )


@router.post(
    "/generate/quick",
    response_model=GenerateSRSResponse,
    tags=["Generation"],
    summary="Quick SRS generation",
    description="Quickly generate an SRS document without validation for faster results"
)
async def quick_generate_srs(request: QuickGenerateRequest):
    """Quick SRS generation without validation."""
    try:
        pipeline = SRSPipeline()
        
        template_name = request.template_name.value if request.template_name else None
        
        result = pipeline.run(
            user_requirement=request.user_requirement,
            template_name=template_name,
            validate=False
        )
        
        return GenerateSRSResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Generation failed: {str(e)}"
        )


@router.post(
    "/validate",
    response_model=ValidateSRSResponse,
    tags=["Validation"],
    summary="Validate SRS document",
    description="Validate an existing SRS document against user requirements and template criteria"
)
async def validate_srs(request: ValidateSRSRequest):
    """Validate an SRS document."""
    try:
        pipeline = SRSPipeline()
        
        result = pipeline.validator.validate(
            srs_document=request.srs_document,
            user_requirement=request.user_requirement,
            template_name=request.template_name.value
        )
        
        return ValidateSRSResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )
