"""Startup SRS Template - Investor and pitch-ready format."""

from typing import Dict, List
from .base_template import BaseSRSTemplate


class StartupSRSTemplate(BaseSRSTemplate):
    """Startup-focused SRS template suitable for investors and pitch decks."""
    
    def __init__(self):
        super().__init__()
        self.name = "startup"
        self.description = "Startup SRS template with business focus, market analysis, and investor-ready documentation"
        self.sections = [
            "Executive Summary",
            "Problem Statement",
            "Solution Overview",
            "Market Analysis",
            "Product Features",
            "Technical Requirements",
            "MVP Scope",
            "Success Metrics",
            "Risks and Mitigations",
            "Roadmap"
        ]
    
    def get_prompt_template(self) -> str:
        return """You are a Product Manager and Software Requirements Engineer with startup experience.

Generate a comprehensive Software Requirements Specification (SRS) document for a startup product:

**User Requirement:**
{user_requirement}

Create a startup-focused SRS that's suitable for investors, stakeholders, and development teams.
Balance business objectives with technical requirements.

Include the following sections:

## 1. Executive Summary
- Product vision (one paragraph)
- Value proposition
- Target market
- Key differentiators

## 2. Problem Statement
- Current pain points
- Market gap
- Why existing solutions fail
- Opportunity size

## 3. Solution Overview
- How the product solves the problem
- Core value proposition
- Key benefits for users
- Competitive advantages

## 4. Market Analysis
- Target audience segments
- Market size (TAM/SAM/SOM if applicable)
- Competitor analysis table:
| Competitor | Strengths | Weaknesses | Our Advantage |
|------------|-----------|------------|---------------|

## 5. Product Features
### Core Features (MVP)
| Feature | User Benefit | Priority |
|---------|--------------|----------|

### Future Features (Post-MVP)
| Feature | User Benefit | Target Release |
|---------|--------------|----------------|

## 6. Technical Requirements

### 6.1 Functional Requirements
- FR-001: [Requirement]
- FR-002: [Requirement]

### 6.2 Non-Functional Requirements
- Performance: [Specific metrics]
- Security: [Requirements]
- Scalability: [Requirements]

### 6.3 Technology Recommendations
- Suggested tech stack
- Third-party integrations

## 7. MVP Scope
- MVP features (absolute minimum)
- MVP timeline estimate
- MVP success criteria
- What's explicitly OUT of MVP scope

## 8. Success Metrics (KPIs)
| Metric | Target | Measurement Method |
|--------|--------|-------------------|

## 9. Risks and Mitigations
| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|---------------------|

## 10. Roadmap
- Phase 1 (MVP): [Timeline and deliverables]
- Phase 2: [Timeline and deliverables]
- Phase 3: [Timeline and deliverables]
- Long-term vision

Use clear, investor-friendly language.
Include tables and bullet points for clarity.
Format the output in clean Markdown."""

    def get_sections(self) -> List[Dict[str, str]]:
        return [
            {"name": "Executive Summary", "description": "Vision, value proposition, target market"},
            {"name": "Problem Statement", "description": "Pain points, market gap, opportunity"},
            {"name": "Solution Overview", "description": "How product solves the problem"},
            {"name": "Market Analysis", "description": "Target audience, market size, competitors"},
            {"name": "Product Features", "description": "Core and future features with priorities"},
            {"name": "Technical Requirements", "description": "Functional and non-functional requirements"},
            {"name": "MVP Scope", "description": "Minimum viable product definition"},
            {"name": "Success Metrics", "description": "KPIs and measurement methods"},
            {"name": "Risks and Mitigations", "description": "Risk analysis and mitigation strategies"},
            {"name": "Roadmap", "description": "Phased development timeline"}
        ]
    
    def get_validation_criteria(self) -> List[str]:
        return [
            "Document must contain all 10 required sections",
            "Executive summary must include: vision, value proposition, target market, differentiators",
            "Problem statement must clearly articulate the market gap",
            "Market analysis must include competitor comparison",
            "Features must be divided into MVP and post-MVP",
            "Functional requirements must be numbered (FR-XXX)",
            "MVP scope must clearly define what's in and out of scope",
            "Success metrics must include measurable KPIs",
            "Risks must include probability, impact, and mitigation",
            "Roadmap must include at least 3 phases",
            "Document must be relevant to the user's original requirement"
        ]
