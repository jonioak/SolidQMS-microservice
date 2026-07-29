from fastapi import APIRouter, HTTPException, status
from typing import List
from app.schemas.prompt import PromptResponse, PromptUpdate
from app.models.prompt import DEFAULT_8D_PROMPTS

router = APIRouter(prefix="/api/v1", tags=["Prompts"])

@router.get("/prompts", response_model=List[PromptResponse])
async def list_prompts():
    """
    Haal alle beschikbare 8D prompt templates op.
    """
    return list(DEFAULT_8D_PROMPTS.values())

@router.get("/prompts/{acht_d_stap}", response_model=PromptResponse)
async def get_prompt(acht_d_stap: str):
    """
    Haal het prompt template op voor een specifieke 8D stap (bijv. D1..D8).
    """
    step = acht_d_stap.upper()
    if step not in DEFAULT_8D_PROMPTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt template voor 8D stap '{acht_d_stap}' niet gevonden."
        )
    return DEFAULT_8D_PROMPTS[step]

@router.put("/prompts/{acht_d_stap}", response_model=PromptResponse)
async def update_prompt(acht_d_stap: str, prompt_update: PromptUpdate):
    """
    Werk een prompt template bij voor een specifieke 8D stap.
    """
    step = acht_d_stap.upper()
    if step not in DEFAULT_8D_PROMPTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt template voor 8D stap '{acht_d_stap}' niet gevonden."
        )
    
    current = DEFAULT_8D_PROMPTS[step]
    updated_data = current.model_copy(update=prompt_update.model_dump(exclude_unset=True))
    DEFAULT_8D_PROMPTS[step] = updated_data
    return updated_data
