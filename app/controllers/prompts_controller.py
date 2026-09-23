from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.schemas.prompt_schema import PromptResponse, PromptUpdate, PromptCreate

import app.crud.prompts as crud_prompts

router = APIRouter(prefix="/prompts", tags=["Prompts"])

@router.get("/", response_model=List[PromptResponse])
async def list_prompts(db: Session = Depends(get_db)):
    """
    Haal alle beschikbare 8D prompt templates op uit de PostgreSQL database.
    """
    return crud_prompts.get_all_prompts(db)


@router.get("/{task_type}", response_model=PromptResponse)
async def get_prompt(task_type: str, db: Session = Depends(get_db)):
    """
    Haal het prompt template op voor een specifieke 8D stap uit de PostgreSQL database.
    """
    prompt = crud_prompts.get_prompt_by_type(db, task_type)
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt template voor '{task_type}' niet gevonden in de database."
        )
    return prompt


@router.post("/create", response_model=PromptResponse)
def create_prompt(
    task_type: str,
    prompt_create: PromptCreate,
    db: Session = Depends(get_db)
):
    """
    Maak een nieuwe prompt template aan in de PostgreSQL database.
    """
    new_prompt = crud_prompts.create_prompt(
        db=db,
        task_type=task_type,
        prompt_create=prompt_create
    )
    return new_prompt


@router.put("/{task_type}", response_model=PromptResponse)
async def update_prompt(
    task_type: str,
    prompt_update: PromptUpdate,
    db: Session = Depends(get_db)
):
    """
    Werk een prompt template bij in de PostgreSQL database.
    """

    prompt_update.task_type = task_type

    updated_prompt = crud_prompts.update_prompt(
        db=db,
        task_type=task_type,
        prompt_update=prompt_update
    )

    if not updated_prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt template voor '{task_type}' niet gevonden in de database."
        )
    
    return updated_prompt
