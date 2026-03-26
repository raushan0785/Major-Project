"""IEEE 830 SRS Template - Standard IEEE format for software requirements."""

from typing import Dict, List
from .base_template import BaseSRSTemplate


class IEEESRSTemplate(BaseSRSTemplate):
    """IEEE 830 Standard SRS template."""
    
    def __init__(self):
        super().__init__()
        self.name = "ieee"
        self.description = "IEEE 830 Standard SRS template - formal documentation suitable for academic and enterprise use"
        self.sections = [
            "Introduction",
            "Overall Description",
            "Specific Requirements",
            "Appendices",
            "Index"
        ]
    
    def get_prompt_template(self) -> str:
        return """You are a Software Requirements Engineer experienced in IEEE 830 Standard documentation.

Generate a comprehensive Software Requirements Specification (SRS) document following IEEE 830 Standard for the following system:

**User Requirement:**
{user_requirement}

Follow IEEE 830 Standard guidelines for software requirements specifications.
The SRS should be formal, comprehensive, and suitable for academic submission and enterprise development.

Include the following sections:

## 1. Introduction

### 1.1 Purpose
- Purpose of this SRS document
- Intended audience and reading suggestions

### 1.2 Scope
- Software product name
- What the software will do and will not do
- Benefits, objectives, and goals

### 1.3 Definitions, Acronyms, and Abbreviations
- All terms used in this document

### 1.4 References
- List of referenced documents

### 1.5 Overview
- Organization of the SRS document

## 2. Overall Description

### 2.1 Product Perspective
- System interfaces
- User interfaces
- Hardware interfaces
- Software interfaces
- Communication interfaces
- Memory constraints
- Operations
- Site adaptation requirements

### 2.2 Product Functions
- Summary of major functions

### 2.3 User Characteristics
- Educational level, experience, and technical expertise of users

### 2.4 Constraints
- Regulatory policies
- Hardware limitations
- Interfaces to other applications
- Parallel operations
- Audit functions
- Control functions
- Higher-order language requirements
- Signal handshake protocols
- Reliability requirements
- Criticality of the application
- Safety and security considerations

### 2.5 Assumptions and Dependencies
- Factors that affect requirements

### 2.6 Apportioning of Requirements
- Requirements that may be delayed until future versions

## 3. Specific Requirements

### 3.1 External Interface Requirements
#### 3.1.1 User Interfaces
#### 3.1.2 Hardware Interfaces
#### 3.1.3 Software Interfaces
#### 3.1.4 Communication Interfaces

### 3.2 Functional Requirements
- Organized by feature, use case, or mode of operation
- Each requirement numbered (REQ-XXX)
- Include: Description, Inputs, Processing, Outputs

### 3.3 Performance Requirements
- Static and dynamic numerical requirements

### 3.4 Design Constraints
- Standards compliance
- Hardware limitations

### 3.5 Software System Attributes
#### 3.5.1 Reliability
#### 3.5.2 Availability
#### 3.5.3 Security
#### 3.5.4 Maintainability
#### 3.5.5 Portability

### 3.6 Other Requirements
- Database requirements
- Internationalization requirements
- Legal requirements
- Reuse objectives

## 4. Appendices
- Supporting information
- Data flow diagrams description
- Analysis models

## 5. Index
- Alphabetical index of key terms

Use formal language, numbered sections, and tables where appropriate.
Format the output in clean Markdown following IEEE documentation standards."""

    def get_sections(self) -> List[Dict[str, str]]:
        return [
            {"name": "Introduction", "description": "Purpose, scope, definitions, references, and overview"},
            {"name": "Overall Description", "description": "Product perspective, functions, user characteristics, constraints"},
            {"name": "Specific Requirements", "description": "External interfaces, functional requirements, performance, design constraints"},
            {"name": "Appendices", "description": "Supporting information and analysis models"},
            {"name": "Index", "description": "Alphabetical index of key terms"}
        ]
    
    def get_validation_criteria(self) -> List[str]:
        return [
            "Document must follow IEEE 830 section structure",
            "Introduction must include: purpose, scope, definitions, references, overview",
            "Overall Description must cover: product perspective, functions, user characteristics, constraints",
            "Specific Requirements must include functional requirements with REQ-XXX numbering",
            "Each functional requirement must have: description, inputs, processing, outputs",
            "Performance requirements must include measurable metrics",
            "Software system attributes must cover: reliability, availability, security, maintainability, portability",
            "Document must use formal technical language",
            "Document must be relevant to the user's original requirement"
        ]
