"""Minimal SRS Template - Quick and concise format for small projects."""

from typing import Dict, List
from .base_template import BaseSRSTemplate


class MinimalSRSTemplate(BaseSRSTemplate):
    """Minimal SRS template for small projects and MVPs."""
    
    def __init__(self):
        super().__init__()
        self.name = "minimal"
        self.description = "Minimal SRS template for small projects, MVPs, and rapid prototyping"
        self.sections = [
            "Project Overview",
            "Features",
            "Requirements",
            "Constraints",
            "Milestones"
        ]
    
    def get_prompt_template(self) -> str:
        return """You are a Software Requirements Engineer specializing in lean documentation.

Generate a concise Software Requirements Specification (SRS) document for the following system:

**User Requirement:**
{user_requirement}

Create a minimal but complete SRS suitable for small projects and MVPs.
Focus on clarity and actionability.

Include the following sections:

## 1. Project Overview
- Project name
- Brief description (2-3 sentences)
- Target users
- Key objectives

## 2. Features
List all features in priority order:
| Priority | Feature | Description |
|----------|---------|-------------|
| P1 (Must Have) | ... | ... |
| P2 (Should Have) | ... | ... |
| P3 (Nice to Have) | ... | ... |

## 3. Requirements

### 3.1 Functional Requirements
- FR-001: [Requirement description]
- FR-002: [Requirement description]
(Continue as needed)

### 3.2 Non-Functional Requirements
- NFR-001: [Performance/Security/Usability requirement]
(Continue as needed)

## 4. Constraints
- Technical constraints
- Time constraints
- Budget constraints (if applicable)
- Dependencies

## 5. Milestones
| Milestone | Description | Target |
|-----------|-------------|--------|
| MVP | ... | ... |
| v1.0 | ... | ... |

Keep the document concise and actionable.
Use bullet points and tables for clarity.
Format the output in clean Markdown."""

    def get_sections(self) -> List[Dict[str, str]]:
        return [
            {"name": "Project Overview", "description": "Name, description, target users, objectives"},
            {"name": "Features", "description": "Prioritized feature list"},
            {"name": "Requirements", "description": "Functional and non-functional requirements"},
            {"name": "Constraints", "description": "Technical, time, and budget constraints"},
            {"name": "Milestones", "description": "Project milestones and targets"}
        ]
    
    def get_validation_criteria(self) -> List[str]:
        return [
            "Document must contain all 5 required sections",
            "Project overview must include: name, description, target users, objectives",
            "Features must be prioritized (P1/P2/P3 or Must Have/Should Have/Nice to Have)",
            "Functional requirements must be numbered (FR-XXX)",
            "Non-functional requirements must be numbered (NFR-XXX)",
            "Constraints section must be present",
            "Milestones must include at least MVP milestone",
            "Document must be relevant to the user's original requirement"
        ]
