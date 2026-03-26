"""Gap analysis and market analysis routes.

These endpoints reuse the existing Gemini-based SRS pipeline (srspipeline-main)
to generate smaller, focused modules instead of a full SRS document.
"""

from __future__ import annotations

import os
import httpx
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ..dependencies import get_current_user

router = APIRouter(prefix="/analysis", tags=["analysis"])


def _normalize_srs_service_url(base_url: str) -> str:
    base = base_url.rstrip("/")
    if base.endswith("/generate/quick") or base.endswith("/generate"):
        return base
    return f"{base}/api/v1/generate/quick"


def _derive_srs_generate_url(service_url: str) -> str:
    url = service_url.rstrip("/")
    if url.endswith("/generate/quick"):
        return url.replace("/generate/quick", "/generate")
    if url.endswith("/generate"):
        return url
    return f"{url}/api/v1/generate"


SRS_SERVICE_URL = _normalize_srs_service_url(
    os.getenv("SRS_SERVICE_URL", "http://127.0.0.1:8001/api/v1/generate/quick")
)
# Prefer explicit SRS_GENERATE_URL env var, else derive from service URL.
SRS_GENERATE_URL = os.getenv("SRS_GENERATE_URL", _derive_srs_generate_url(SRS_SERVICE_URL))


class AnalysisRequest(BaseModel):
    input_text: str = Field(..., min_length=10, description="User requirements / prompt text")


class AnalysisResponse(BaseModel):
    message: str
    analysis_text: str
    module_name: str


def _build_gap_prompt_instructions() -> str:
    return (
        "Create the Gap Analysis Module.\n"
        "Task: Identify challenges and missing features in the CURRENT solution based on the provided requirements.\n"
        "Output rules:\n"
        "- Output ONLY this module (no extra SRS sections).\n"
        "- Start with the heading exactly: 'Gap Analysis Module'.\n"
        "- Use 3 concise bullet lists with these headings:\n"
        "  1) Challenges\n"
        "  2) Missing Features\n"
        "  3) Risks / Assumptions\n"
        "- Keep wording clear and suitable for SRS usage.\n"
        "- Do not invent statistics or market numbers.\n"
        "- If something is not specified in the input, write 'Not specified'."
    )


def _build_market_prompt_instructions() -> str:
    return (
        "Create the Market Analysis Module.\n"
        "Task: Provide market context based on the provided requirements.\n"
        "Output rules:\n"
        "- Output ONLY this module (no extra SRS sections).\n"
        "- Start with the heading exactly: 'Market Analysis Module'.\n"
        "- Include these parts in order:\n"
        "  1) Executive Summary\n"
        "  2) Target Market\n"
        "  3) Market Size (qualitative)\n"
        "  4) Competitors (types)\n"
        "  5) Market Gap\n"
        "  6) Go-to-Market Notes\n"
        "- Do not invent statistics. Use qualitative statements; if not provided, write 'Not specified'."
    )


async def _call_srs_pipeline(
    *,
    input_text: str,
    module_name: str,
    custom_instructions: str,
) -> str:
    payload = {
        "user_requirement": input_text,
        # Template name mostly controls the base prompt; we override output via custom_instructions.
        # Startup tends to include market-related guidance.
        "template_name": "startup" if module_name == "market" else "minimal",
        "custom_instructions": custom_instructions,
        "validate": False,
        "auto_fix": False,
    }

    endpoints_to_try = [SRS_GENERATE_URL]
    if SRS_SERVICE_URL not in endpoints_to_try:
        endpoints_to_try.append(SRS_SERVICE_URL)

    response = None
    last_error = None

    async with httpx.AsyncClient(timeout=300.0) as client:
        for endpoint in endpoints_to_try:
            try:
                response = await client.post(endpoint, json=payload)
                if response.status_code == 404:
                    last_error = response.text
                    continue
                break
            except httpx.RequestError as exc:
                last_error = f"Could not connect to SRS pipeline ({type(exc).__name__}): {exc}"
                continue

    if response is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"SRS pipeline unavailable: {last_error}",
        )

    if response.status_code == 404:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"SRS pipeline endpoint not found (tried {endpoints_to_try}): {response.text}",
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"SRS pipeline returned error: {response.text}",
        )

    srs_data = response.json()
    if not srs_data.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SRS analysis generation failed: {srs_data.get('error')}",
        )

    return srs_data.get("srs_document") or ""


@router.post("/gap", response_model=AnalysisResponse)
async def generate_gap_analysis(
    request: AnalysisRequest,
    current_user: dict = Depends(get_current_user),
):
    analysis_text = await _call_srs_pipeline(
        input_text=request.input_text,
        module_name="gap",
        custom_instructions=_build_gap_prompt_instructions(),
    )
    return AnalysisResponse(
        message="Gap analysis generated successfully",
        analysis_text=analysis_text,
        module_name="gap",
    )


@router.post("/market", response_model=AnalysisResponse)
async def generate_market_analysis(
    request: AnalysisRequest,
    current_user: dict = Depends(get_current_user),
):
    analysis_text = await _call_srs_pipeline(
        input_text=request.input_text,
        module_name="market",
        custom_instructions=_build_market_prompt_instructions(),
    )
    return AnalysisResponse(
        message="Market analysis generated successfully",
        analysis_text=analysis_text,
        module_name="market",
    )

