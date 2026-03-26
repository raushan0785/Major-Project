"""Agile SRS Template - Scrum/Kanban focused template."""

from typing import Dict, List
from .base_template import BaseSRSTemplate


class AgileSRSTemplate(BaseSRSTemplate):
    """Agile-focused SRS template with user stories and sprint planning."""
    
    def __init__(self):
        super().__init__()
        self.name = "agile"
        self.description = "Agile methodology SRS template with user stories, sprint planning, and iterative development focus"
        self.sections = [
            "Introduction",
            "Agile Overview",
            "User Personas",
            "Product Backlog",
            "Functional Requirements",
            "Non-Functional Requirements",
            "Sprint Planning",
            "Constraints and Assumptions",
            "Requirement Traceability Matrix",
            "Future Enhancements"
        ]
    
    def get_prompt_template(self) -> str:
        return """You are a Software Requirements Engineer experienced in Agile methodology.

Generate an extensive Software Requirements Specification (SRS) document in Agile format for the following system:

**User Requirement:**
{user_requirement}

Follow Agile principles (iterative development, customer focus, adaptability).
The SRS should be clear, structured, and suitable for academic submission and real-world development.

Include the following sections:

## 1. Introduction
- Purpose of the document
- Scope of the system
- Definitions, acronyms, and abbreviations
- References

## 2. Agile Overview
- Agile approach used (Scrum / Kanban / Hybrid)
- Product vision
- Stakeholders
- Agile roles (Product Owner, Scrum Master, Development Team)

## 3. User Personas
- Description of different user types with demographics, goals, and pain points

## 4. Product Backlog (User Stories)
- User stories in the format: As a [user], I want [feature], so that [benefit]
- Priority (High / Medium / Low)
- Story points estimation
- Acceptance criteria for each user story

## 5. Functional Requirements
- Derived from user stories
- Clearly numbered and traceable (FR-001, FR-002, etc.)

## 6. Non-Functional Requirements
- Performance (response times, throughput)
- Security (authentication, authorization, data protection)
- Usability (accessibility, user experience)
- Scalability (horizontal/vertical scaling)
- Reliability (uptime, fault tolerance)

## 7. Sprint Planning Overview
- Sprint duration
- Sample sprint backlog for first 2-3 sprints
- Release planning summary
- Definition of Done

## 8. System Constraints and Assumptions
- Technical constraints
- Business constraints
- Assumptions

## 9. Requirement Traceability Matrix (RTM)
- Mapping user stories to functional requirements
- Use table format

## 10. Future Enhancements
- Features planned for later iterations
- Technical debt items

Use simple language, bullet points, and tables where appropriate.
Format the output in clean Markdown."""

    def get_sections(self) -> List[Dict[str, str]]:
        return [
            {"name": "Introduction", "description": "Purpose, scope, definitions, and references"},
            {"name": "Agile Overview", "description": "Agile approach, vision, stakeholders, and roles"},
            {"name": "User Personas", "description": "Different user types with demographics and goals"},
            {"name": "Product Backlog", "description": "User stories with priority and acceptance criteria"},
            {"name": "Functional Requirements", "description": "Numbered requirements derived from user stories"},
            {"name": "Non-Functional Requirements", "description": "Performance, security, usability, scalability, reliability"},
            {"name": "Sprint Planning", "description": "Sprint duration, backlog, and release planning"},
            {"name": "Constraints and Assumptions", "description": "Technical and business constraints"},
            {"name": "RTM", "description": "Requirement Traceability Matrix"},
            {"name": "Future Enhancements", "description": "Planned features for later iterations"}
        ]
    
    def get_validation_criteria(self) -> List[str]:
        return [
            "Document must contain all 10 required sections",
            "User stories must follow 'As a [user], I want [feature], so that [benefit]' format",
            "Each user story must have priority and acceptance criteria",
            "Functional requirements must be numbered (FR-XXX format)",
            "Non-functional requirements must cover: performance, security, usability, scalability, reliability",
            "Sprint planning must include sprint duration and sample backlog",
            "RTM must map user stories to functional requirements",
            "Document must be relevant to the user's original requirement"
        ]
