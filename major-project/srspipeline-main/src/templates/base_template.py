"""Base template class for SRS templates."""

from abc import ABC, abstractmethod
from typing import Dict, List


class BaseSRSTemplate(ABC):
    """Abstract base class for all SRS templates."""
    
    def __init__(self):
        self.name: str = ""
        self.description: str = ""
        self.sections: List[str] = []
    
    @abstractmethod
    def get_prompt_template(self) -> str:
        """Return the prompt template for SRS generation."""
        pass
    
    @abstractmethod
    def get_sections(self) -> List[Dict[str, str]]:
        """Return list of sections with their descriptions."""
        pass
    
    @abstractmethod
    def get_validation_criteria(self) -> List[str]:
        """Return validation criteria for this template."""
        pass
    
    def get_metadata(self) -> Dict[str, str]:
        """Return template metadata."""
        return {
            "name": self.name,
            "description": self.description,
            "section_count": len(self.sections)
        }
