# """Grammar correction router - Suggests grammatically correct versions of input text."""

# import os
# from pathlib import Path
# import requests
# import json
# from typing import Optional, List
# from fastapi import APIRouter, Depends, HTTPException, status
# from pydantic import BaseModel

# from ..dependencies import get_current_user
# from dotenv import load_dotenv

# # Always load the module's owning ProjectBackend1/.env (independent of CWD),
# # so Gemini key is reliably available when this router is imported.
# _ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
# load_dotenv(dotenv_path=_ENV_PATH, override=True)

# router = APIRouter(prefix="/grammar", tags=["grammar"])


# class GrammarCorrectionRequest(BaseModel):
#     """Request model for grammar correction."""
#     text: str = ...  # The text to be corrected
#     num_suggestions: Optional[int] = 3  # Number of suggestions (default: 3, max: 5)

#     class Config:
#         schema_extra = {
#             "example": {
#                 "text": "i want to build a app which help user to order food online",
#                 "num_suggestions": 3
#             }
#         }


# class CorrectedOption(BaseModel):
#     """A single corrected version of the text."""
#     option_number: int
#     corrected_text: str
#     explanation: Optional[str] = None


# class GrammarCorrectionResponse(BaseModel):
#     """Response model for grammar correction."""
#     original_text: str
#     suggestions: List[CorrectedOption]
#     message: str


# def _correct_grammar_with_gemini(
#     text: str,
#     num_suggestions: int = 3
# ) -> List[CorrectedOption]:
#     """
#     Use Gemini API to generate grammatically correct versions of the input text.
#     Uses REST API for better reliability.
    
#     Args:
#         text: The input text to be corrected
#         num_suggestions: Number of suggestions to generate (1-5)
    
#     Returns:
#         List of corrected options
#     """
#     api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
#     if not api_key:
#         print("[Grammar] Gemini API key not configured, using fallback grammar correction.")
#         return _fallback_grammar_corrections(text, num_suggestions)
    
#     # Clamp num_suggestions between 1 and 5
#     num_suggestions = max(1, min(5, num_suggestions))
    
#     prompt = f"""You are an expert English writing assistant for software requirements.
# Generate {num_suggestions} improved prompt options that are grammatically correct and easy for an SRS generation AI to understand.

# Original text: "{text}"

# Requirements:
# 1. Keep the original meaning and intent exactly.
# 2. Fix grammar, punctuation, and sentence clarity.
# 3. Rewrite as clear software requirement text.
# 4. Make each option slightly different in style (concise, structured, formal).
# 5. Do NOT add new features or assumptions not present in original text.
# 6. Keep each option short, direct, and unambiguous for SRS generation.

# Format your response EXACTLY as follows (use this exact format):
# OPTION 1: [corrected text here]
# EXPLANATION 1: [brief explanation of the correction]
# OPTION 2: [corrected text here]
# EXPLANATION 2: [brief explanation of the correction]
# OPTION 3: [corrected text here]
# EXPLANATION 3: [brief explanation of the correction]

# If generating fewer than {num_suggestions} options, still use the same format but with fewer options.
# """
    
#     try:
#         configured_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
#         candidate_models = [
#             configured_model,
#             # Common working variants if the configured model name isn't enabled for your key.
#             "gemini-2.5-flash",
#             "gemini-2.5-flash-latest",
#             "gemini-2.5-pro",
#             "gemini-1.5-flash-latest",
#             "gemini-1.5-pro",
#             "gemini-1.0-pro",
#         ]

#         headers = {"Content-Type": "application/json"}
#         payload = {
#             "contents": [
#                 {
#                     "parts": [
#                         {"text": prompt}
#                     ]
#                 }
#             ]
#         }

#         last_error: Optional[str] = None
#         candidate_api_bases = [
#             "https://generativelanguage.googleapis.com/v1beta",
#             "https://generativelanguage.googleapis.com/v1",
#         ]

#         for api_base in candidate_api_bases:
#             for model in candidate_models:
#                 print(f"[Grammar] Calling Gemini REST API with base={api_base}, model: {model}")

#                 # Use the REST API endpoint
#                 url = f"{api_base}/models/{model}:generateContent?key={api_key}"

#                 print(f"[Grammar] Sending request to {url[:80]}...")
#                 response = requests.post(url, json=payload, headers=headers, timeout=30)

#                 print(f"[Grammar] API response status: {response.status_code}")
#                 if response.status_code == 200:
#                     response_data = response.json()
#                     print(f"[Grammar] Got response, parsing...")

#                     if "candidates" not in response_data or not response_data["candidates"]:
#                         raise ValueError("No candidates in response")

#                     response_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
#                     print(f"[Grammar] Response text length: {len(response_text)}")

#                     corrections = _parse_gemini_response(response_text, num_suggestions)
#                     print(f"[Grammar] Parsed {len(corrections)} corrections")
#                     return corrections

#                 # If the model name isn't found for this API version/key, retry next model/base.
#                 last_error = response.text
#                 if response.status_code == 404:
#                     print(f"[Grammar] Not found (404). Trying next model/base. Response: {last_error[:200]}")
#                     continue

#                 # For other HTTP errors, fail fast (and fallback later).
#                 print(f"[Grammar] API error response: {last_error[:500]}")
#                 raise HTTPException(
#                     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                     detail=f"Gemini API error ({response.status_code}): {last_error[:200]}"
#                 )

#         # If we reach here, all models failed.
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"All Gemini model attempts failed. Last error: {str(last_error)[:200]}"
#         )
    
#     except requests.exceptions.RequestException as e:
#         error_msg = f"Network error: {str(e)}"
#         print(f"[Grammar] {error_msg}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=error_msg
#         )
#     except ValueError as e:
#         error_msg = f"Invalid response format: {str(e)}"
#         print(f"[Grammar] {error_msg}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=error_msg
#         )
#     except Exception as e:
#         error_msg = f"Error during grammar correction: {type(e).__name__}: {str(e)}"
#         print(f"[Grammar] {error_msg}")
#         import traceback
#         traceback.print_exc()
#         # fallback to local correction instead of hard failing
#         return _fallback_grammar_corrections(text, num_suggestions)


# def _fallback_grammar_corrections(text: str, num_suggestions: int = 3) -> List[CorrectedOption]:
#     """Fallback grammar correction when Gemini API is unavailable."""
#     corrected = text.strip()

#     # Basic text normalization
#     if corrected:
#         corrected = corrected[0].upper() + corrected[1:]
#     corrected = corrected.replace(" a app", " an app").replace(" a user", " a single user")

#     suggestions: List[CorrectedOption] = []
#     for i in range(1, min(num_suggestions, 5) + 1):
#         if i == 1:
#             suggestion_text = corrected
#             explanation = "Capitalized sentence and fixed article usage."
#         elif i == 2:
#             suggestion_text = corrected.replace("I want", "I would like").replace("i want", "I would like")
#             explanation = "More polite phrasing."
#         else:
#             suggestion_text = corrected
#             explanation = "Alternative phrasing with equivalent meaning."

#         if not suggestion_text:
#             suggestion_text = text.strip()
#             explanation = "Original text returned as fallback."

#         suggestions.append(CorrectedOption(option_number=i, corrected_text=suggestion_text, explanation=explanation))

#     return suggestions


# def _parse_gemini_response(response_text: str, max_options: int) -> List[CorrectedOption]:
#     """
#     Parse Gemini's response to extract corrected options.
    
#     Args:
#         response_text: The raw response from Gemini
#         max_options: Maximum number of options to extract
    
#     Returns:
#         List of CorrectedOption objects
#     """
#     corrections = []
#     lines = response_text.strip().split('\n')
    
#     option_num = 1
#     current_option_text = None
#     current_explanation = None
    
#     for line in lines:
#         line = line.strip()
        
#         if line.startswith(f"OPTION {option_num}:"):
#             if current_option_text and option_num <= max_options:
#                 # Save previous option
#                 corrections.append(
#                     CorrectedOption(
#                         option_number=option_num - 1,
#                         corrected_text=current_option_text,
#                         explanation=current_explanation
#                     )
#                 )
#             # Extract new option
#             current_option_text = line.replace(f"OPTION {option_num}:", "").strip()
#             current_explanation = None
            
#         elif line.startswith(f"EXPLANATION {option_num}:"):
#             current_explanation = line.replace(f"EXPLANATION {option_num}:", "").strip()
#             option_num += 1
    
#     # Add the last option
#     if current_option_text and option_num <= max_options + 1:
#         corrections.append(
#             CorrectedOption(
#                 option_number=option_num - 1,
#                 corrected_text=current_option_text,
#                 explanation=current_explanation
#             )
#         )
    
#     # If parsing failed, create a simple fallback
#     if not corrections:
#         corrections.append(
#             CorrectedOption(
#                 option_number=1,
#                 corrected_text=response_text.split('\n')[0],
#                 explanation="Grammar corrected version"
#             )
#         )
    
#     return corrections


# @router.post("/correct", response_model=GrammarCorrectionResponse)
# async def correct_grammar(
#     request: GrammarCorrectionRequest,
#     current_user: dict = Depends(get_current_user)
# ):
#     """
#     Correct grammar and suggest alternative phrasings for the input text.
    
#     Args:
#         request: GrammarCorrectionRequest containing the text to correct
#         current_user: Current authenticated user
    
#     Returns:
#         GrammarCorrectionResponse with suggested corrections
#     """
#     # Validate input
#     if not request.text or len(request.text.strip()) < 3:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Input text must be at least 3 characters long"
#         )
    
#     # Get corrections using REST API
#     suggestions = _correct_grammar_with_gemini(
#         text=request.text,
#         num_suggestions=request.num_suggestions
#     )
    
#     return GrammarCorrectionResponse(
#         original_text=request.text,
#         suggestions=suggestions,
#         message=f"Generated {len(suggestions)} grammar correction suggestion(s)"
#     )


# @router.post("/suggest-prompts", response_model=GrammarCorrectionResponse)
# async def suggest_prompts_for_srs(
#     request: GrammarCorrectionRequest,
#     current_user: dict = Depends(get_current_user)
# ):
#     """
#     Return exactly 3 improved prompt suggestions optimized for SRS generation.
#     """
#     if not request.text or len(request.text.strip()) < 3:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Input text must be at least 3 characters long"
#         )

#     suggestions = _correct_grammar_with_gemini(
#         text=request.text,
#         num_suggestions=3
#     )

#     return GrammarCorrectionResponse(
#         original_text=request.text,
#         suggestions=suggestions[:3],
#         message="Generated 3 improved prompt suggestion(s) for SRS generation"
#     )


# @router.post("/quick-check")
# async def quick_grammar_check(
#     request: GrammarCorrectionRequest,
#     current_user: dict = Depends(get_current_user)
# ):
#     """
#     Quick grammar check endpoint that returns suggestions without detailed explanations.
#     Useful for fast feedback loops.
    
#     Args:
#         request: GrammarCorrectionRequest containing the text to check
#         current_user: Current authenticated user
    
#     Returns:
#         List of suggested corrections
#     """
#     if not request.text or len(request.text.strip()) < 3:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Input text must be at least 3 characters long"
#         )
    
#     suggestions = _correct_grammar_with_gemini(
#         text=request.text,
#         num_suggestions=min(3, request.num_suggestions)
#     )
    
#     return {
#         "original": request.text,
#         "suggestions": [s.corrected_text for s in suggestions]
#     }
"""Grammar correction router - Suggests grammatically correct versions of input text."""

import os
from pathlib import Path
import requests
import json
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..dependencies import get_current_user
from dotenv import load_dotenv

# Load .env
_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=_ENV_PATH, override=True)

router = APIRouter(prefix="/grammar", tags=["grammar"])


# ========================= MODELS ========================= #

class GrammarCorrectionRequest(BaseModel):
    text: str
    num_suggestions: Optional[int] = 3


class CorrectedOption(BaseModel):
    option_number: int
    corrected_text: str
    explanation: Optional[str] = None


class GrammarCorrectionResponse(BaseModel):
    original_text: str
    suggestions: List[CorrectedOption]
    message: str


# ========================= CORE LOGIC ========================= #

def _correct_grammar_with_gemini(text: str, num_suggestions: int = 3) -> List[CorrectedOption]:
    api_key = os.getenv("GOOGLE_GEMINI_API_KEY")

    if not api_key:
        print("[Grammar] No API key → using fallback")
        return _fallback(text, num_suggestions)

    num_suggestions = max(1, min(5, num_suggestions))

    prompt = f"""
Improve the following user input and generate {num_suggestions} DIFFERENT improved versions.

Text:
"{text}"

Rules:
- Fix grammar, spelling, clarity
- Keep same meaning
- Make it suitable for SRS generation
- Each version MUST be different

Return ONLY JSON:
[
  {{"option": 1, "text": "...", "explanation": "..."}},
  {{"option": 2, "text": "...", "explanation": "..."}},
  {{"option": 3, "text": "...", "explanation": "..."}}
]
"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.8,
            "topP": 0.9
        }
    }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

    try:
        response = requests.post(url, json=payload, timeout=30)

        if response.status_code != 200:
            print("[Grammar API ERROR]:", response.text)
            return _fallback(text, num_suggestions)

        data = response.json()
        response_text = data["candidates"][0]["content"]["parts"][0]["text"]

        print("\n===== GEMINI RESPONSE =====\n", response_text)

        return _parse_json_response(response_text, num_suggestions)

    except Exception as e:
        print("[Grammar ERROR]:", str(e))
        return _fallback(text, num_suggestions)


# ========================= PARSER ========================= #

def _parse_json_response(response_text: str, max_options: int) -> List[CorrectedOption]:
    try:
        parsed = json.loads(response_text)

        results = []
        for i, item in enumerate(parsed[:max_options]):
            results.append(
                CorrectedOption(
                    option_number=item.get("option", i + 1),
                    corrected_text=item.get("text", ""),
                    explanation=item.get("explanation", "")
                )
            )

        return results

    except Exception as e:
        print("[Parse Error]:", str(e))
        return _fallback(response_text, max_options)


# ========================= FALLBACK ========================= #

def _fallback(text: str, num_suggestions: int = 3) -> List[CorrectedOption]:
    text = text.strip()

    if text:
        text = text[0].upper() + text[1:]

    variations = [
        text,
        text.replace("want", "would like"),
        f"The user requires: {text}"
    ]

    results = []

    for i in range(min(num_suggestions, len(variations))):
        results.append(
            CorrectedOption(
                option_number=i + 1,
                corrected_text=variations[i],
                explanation="Fallback improvement"
            )
        )

    return results


# ========================= ROUTES ========================= #

@router.post("/correct", response_model=GrammarCorrectionResponse)
async def correct_grammar(
    request: GrammarCorrectionRequest,
    current_user: dict = Depends(get_current_user)
):
    if not request.text or len(request.text.strip()) < 3:
        raise HTTPException(status_code=400, detail="Text too short")

    suggestions = _correct_grammar_with_gemini(
        request.text,
        request.num_suggestions
    )

    return GrammarCorrectionResponse(
        original_text=request.text,
        suggestions=suggestions,
        message=f"{len(suggestions)} suggestions generated"
    )


@router.post("/quick-check")
async def quick_check(
    request: GrammarCorrectionRequest,
    current_user: dict = Depends(get_current_user)
):
    suggestions = _correct_grammar_with_gemini(
        request.text,
        min(3, request.num_suggestions)
    )

    return {
        "original": request.text,
        "suggestions": [s.corrected_text for s in suggestions]
    }


# ✅ FINAL FIXED ROUTE (THIS WAS MISSING)

@router.post("/suggest-prompts", response_model=GrammarCorrectionResponse)
async def suggest_prompts_for_srs(
    request: GrammarCorrectionRequest,
    current_user: dict = Depends(get_current_user)
):
    if not request.text or len(request.text.strip()) < 3:
        raise HTTPException(
            status_code=400,
            detail="Input text must be at least 3 characters long"
        )

    suggestions = _correct_grammar_with_gemini(
        text=request.text,
        num_suggestions=3
    )

    return GrammarCorrectionResponse(
        original_text=request.text,
        suggestions=suggestions[:3],
        message="Generated 3 improved prompts"
    )