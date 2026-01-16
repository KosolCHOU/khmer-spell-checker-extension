from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager
import sys
from pathlib import Path

# Add the current directory to sys.path to ensure keyez can be imported if needed
# (Though usually implicit)
BASE_PATH = Path(__file__).resolve().parent
sys.path.append(str(BASE_PATH))

# Import the core logic from the shared module
from keyez.landing.spell_checker_advanced import (
    check_spelling, 
    SpellCheckerData
)

# --- FastAPI Models ---

class CheckRequest(BaseModel):
    text: str

class Suggestion(BaseModel):
    word: str
    score: float

class ErrorResult(BaseModel):
    token: str
    index: int
    suggestions: List[Suggestion]

class CheckResponse(BaseModel):
    original_text: str
    tokens: List[str]
    errors: List[ErrorResult]

# --- Lifecycle & App ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pre-load resources
    print("Loading spell checker data...")
    SpellCheckerData.build_tables()
    SpellCheckerData.load_bigrams()
    print("Spell checker data loaded.")
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Endpoints ---

@app.post("/check", response_model=CheckResponse)
@app.post("/api/spell-check/", response_model=CheckResponse)
def check_text_api(req: CheckRequest):
    # Use the shared logic
    result = check_spelling(req.text)
    
    if not result.get('success'):
        # Pass through error from the logic
        raise HTTPException(status_code=500, detail=result.get('error', 'Unknown error'))
    
    tokens = result['tokens']
    errors_dict = result['errors']
    
    formatted_errors = []
    # Sort errors by index for stable output
    for idx_str in sorted(errors_dict.keys(), key=lambda x: int(x)):
        # Indexes are keys (integers or stringified integers)
        idx = int(idx_str)
        err_data = errors_dict[idx]
        
        sugs = []
        # The suggestions in result are List[str] or similar
        # We need to wrap them in Suggestion(word=..., score=...)
        # We synthesize a score if individual scores are missing, 
        # using the error's overall confidence.
        base_confidence = err_data.get('confidence', 0.8)
        
        suggestion_list = err_data.get('suggestions', [])
        for i, s_word in enumerate(suggestion_list):
            # Degrading score for subsequent options
            score = base_confidence * (0.9 ** i)
            sugs.append(Suggestion(word=s_word, score=score))
            
        formatted_errors.append(ErrorResult(
            token=err_data['original'],
            index=idx,
            suggestions=sugs
        ))
        
    return CheckResponse(
        original_text=req.text,
        tokens=tokens,
        errors=formatted_errors
    )

class TransliterateRequest(BaseModel):
    text: str

@app.post("/transliterate/")
def transliterate_api(req: TransliterateRequest):
    try:
        from keyez.landing.transliterator import get_transliterator
        transliterator = get_transliterator()
        candidates = transliterator.translate(req.text, top_k=3)
        
        while len(candidates) < 3:
            candidates.append('')
            
        return {
            'candidates': [
                candidates[1] if len(candidates) > 1 else '',  # Left (2nd best)
                candidates[0] if len(candidates) > 0 else '',  # Middle (best)
                candidates[2] if len(candidates) > 2 else ''   # Right (3rd best)
            ],
            'success': True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def health_check():
    return {"status": "ok", "service": "Advanced Khmer Spelling API (Shared Logic)"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
