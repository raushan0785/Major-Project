"""Template Registry - Central registry for all SRS templates."""

from typing import Dict, List, Optional, Type
from .base_template import BaseSRSTemplate
from .agile_template import AgileSRSTemplate
from .ieee_template import IEEESRSTemplate
from .minimal_template import MinimalSRSTemplate
from .startup_template import StartupSRSTemplate


class TemplateRegistry:
    """Central registry for managing SRS templates."""
    
    _templates: Dict[str, Type[BaseSRSTemplate]] = {
        "agile": AgileSRSTemplate,
        "ieee": IEEESRSTemplate,
        "minimal": MinimalSRSTemplate,
        "startup": StartupSRSTemplate
    }
    
    @classmethod
    def get_template(cls, template_name: str) -> Optional[BaseSRSTemplate]:
        """Get a template instance by name."""
        template_class = cls._templates.get(template_name.lower())
        if template_class:
            return template_class()
        return None
    
    @classmethod
    def list_templates(cls) -> List[Dict[str, str]]:
        """List all available templates with their metadata."""
        templates = []
        for name, template_class in cls._templates.items():
            instance = template_class()
            templates.append({
                "name": name,
                "description": instance.description,
                "sections": instance.sections
            })
        return templates
    
    @classmethod
    def get_template_names(cls) -> List[str]:
        """Get list of all template names."""
        return list(cls._templates.keys())
    
    @classmethod
    def register_template(cls, name: str, template_class: Type[BaseSRSTemplate]) -> None:
        """Register a new template."""
        cls._templates[name.lower()] = template_class
    
    @classmethod
    def get_template_for_requirement(cls, requirement: str) -> str:
        """Suggest a template based on the requirement content."""
        requirement_lower = requirement.lower()
        
        # Check for explicit template mentions
        if "ieee" in requirement_lower or "formal" in requirement_lower or "academic" in requirement_lower:
            return "ieee"
        elif "startup" in requirement_lower or "investor" in requirement_lower or "pitch" in requirement_lower:
            return "startup"
        elif "minimal" in requirement_lower or "quick" in requirement_lower or "mvp" in requirement_lower or "simple" in requirement_lower:
            return "minimal"
        elif "agile" in requirement_lower or "scrum" in requirement_lower or "sprint" in requirement_lower or "user story" in requirement_lower:
            return "agile"
        
        # Default to agile as it's most commonly used
        return "agile"


# Convenience functions for direct access
def get_template(template_name: str) -> Optional[BaseSRSTemplate]:
    """Get a template instance by name."""
    return TemplateRegistry.get_template(template_name)


def list_templates() -> List[Dict[str, str]]:
    """List all available templates."""
    return TemplateRegistry.list_templates()
