"""SRS Pipeline - Main FastAPI Application.

This application provides a complete SRS (Software Requirements Specification) 
generation pipeline using Google Gemini AI with validation capabilities.

API Documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json
"""



from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import uvicorn

from src.api import router

# Create FastAPI application with OpenAPI documentation
app = FastAPI(
    title="SRS Generation Pipeline",
    description="""
## 🚀 SRS Generation Pipeline API

A comprehensive API for generating and validating Software Requirements Specification (SRS) documents using AI.

### Features:
- **Multiple Templates**: Choose from Agile, IEEE 830, Minimal, or Startup templates
- **AI-Powered Generation**: Uses Google Gemini AI for intelligent SRS generation
- **Validation**: Cross-check generated SRS against requirements and template criteria
- **Auto-Fix**: Automatically improve SRS documents based on validation feedback
- **Template Suggestion**: Get AI-recommended template based on your requirements

### Templates Available:
| Template | Best For |
|----------|----------|
| **Agile** | Scrum/Kanban projects with user stories and sprints |
| **IEEE** | Formal academic or enterprise documentation |
| **Minimal** | MVPs, small projects, rapid prototyping |
| **Startup** | Investor-ready, pitch deck supporting documentation |

### Quick Start:
1. List templates: `GET /api/v1/templates`
2. Generate SRS: `POST /api/v1/generate`
3. Validate SRS: `POST /api/v1/validate`

### Environment Variables Required:
- `GOOGLE_GEMINI_API_KEY`: Your Google Gemini API key
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "SRS Pipeline Support",
        "email": "support@example.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    openapi_tags=[
        {
            "name": "Health",
            "description": "Health check endpoints"
        },
        {
            "name": "Templates",
            "description": "SRS template management and suggestions"
        },
        {
            "name": "Generation",
            "description": "SRS document generation endpoints"
        },
        {
            "name": "Validation",
            "description": "SRS document validation endpoints"
        }
    ]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")


@app.get("/", include_in_schema=False)
async def root():
    """Redirect to API documentation."""
    return RedirectResponse(url="/docs")


@app.get("/api", include_in_schema=False)
async def api_root():
    """API information endpoint."""
    return {
        "message": "Welcome to SRS Generation Pipeline API",
        "version": "1.0.0",
        "documentation": "/docs",
        "openapi": "/openapi.json",
        "endpoints": {
            "templates": "/api/v1/templates",
            "generate": "/api/v1/generate",
            "validate": "/api/v1/validate",
            "health": "/api/v1/health"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8001, 
        reload=True,
        log_level="info"
    )