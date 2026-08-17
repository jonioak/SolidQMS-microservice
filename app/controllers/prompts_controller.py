from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.schemas.prompt import PromptResponse, PromptUpdate

import app.crud.prompts as crud

router = APIRouter(prefix="/api/v1", tags=["Prompts"])


@router.get("/prompts", response_model=List[PromptResponse])
async def list_prompts(db: Session = Depends(get_db)):
    """
    Haal alle beschikbare 8D prompt templates op uit de PostgreSQL database.
    """
    return crud.get_all_prompts(db)


@router.get("/prompts/{acht_d_stap}", response_model=PromptResponse)
async def get_prompt(acht_d_stap: str, db: Session = Depends(get_db)):
    """
    Haal het prompt template op voor een specifieke 8D stap uit de PostgreSQL database.
    """
    prompt = crud.get_prompt_by_step(db, acht_d_stap)
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt template voor '{acht_d_stap}' niet gevonden in de database."
        )
    return prompt


@router.put("/prompts/{acht_d_stap}", response_model=PromptResponse)
async def update_prompt(acht_d_stap: str, prompt_update: PromptUpdate, is_active: bool, db: Session = Depends(get_db)):
    """
    Werk een prompt template bij in de PostgreSQL database.
    """
    updated_prompt = crud.update_prompt(
        db=db,
        step_code=acht_d_stap,
        template_text=prompt_update.title,
        description=prompt_update.description,
        is_active=is_active,
        system_prompt=prompt_update.system_prompt
    )

    if not updated_prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt template voor '{acht_d_stap}' niet gevonden in de database."
        )
    
    return updated_prompt
