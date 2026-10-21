from fastapi import APIRouter, HTTPException, Depends, status
from typing import List

from app.interfaces.repositories import IPromptRepository
from app.dependencies import get_prompt_repository
from app.schemas.prompt_schema import PromptResponse, PromptUpdate, PromptCreate

router = APIRouter(prefix="/prompts", tags=["Prompts"])


@router.get("/", response_model=List[PromptResponse])
async def list_prompts(prompt_repo: IPromptRepository = Depends(get_prompt_repository)):
    return prompt_repo.get_all()


@router.get("/{task_type}", response_model=PromptResponse)
async def get_prompt(
    task_type: str,
    prompt_repo: IPromptRepository = Depends(get_prompt_repository)
):
    prompt = prompt_repo.get_by_type(task_type)
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
    prompt_repo: IPromptRepository = Depends(get_prompt_repository)
):
    new_prompt = prompt_repo.create(
        task_type=task_type,
        prompt_create=prompt_create
    )
    return new_prompt


@router.put("/{task_type}", response_model=PromptResponse)
async def update_prompt(
    task_type: str,
    prompt_update: PromptUpdate,
    prompt_repo: IPromptRepository = Depends(get_prompt_repository)
):
    updated_prompt = prompt_repo.update(
        task_type=task_type,
        prompt_update=prompt_update
    )

    if not updated_prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt template voor '{task_type}' niet gevonden in de database."
        )
    
    return updated_prompt
