from fastapi import APIRouter, BackgroundTasks, status, Depends, HTTPException

from app.db.database import SessionLocal

from app.schemas.task_schema import TaskBase, TaskResponse
from app.services.ai_client import AIService

from typing import List, Dict, Any

from sqlalchemy.orm import Session
from app.db.database import get_db

from app.models.prompt import PromptTemplate

import app.crud.tasks as crud_tasks
import app.crud.prompts as crud_prompts

router = APIRouter(prefix="/api/v1", tags=["tasks"])
ai_service = AIService()

@router.post("/ai", response_model=TaskResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_ai_suggestion(request: TaskBase, db: Session = Depends(get_db)):

    # Haal de prompt op via de CRUD-laag
    prompt = crud_prompts.get_prompt_by_step(db, step_code=request.step_code)
    
    if not prompt:
        raise HTTPException(status_code=404, detail=f"Prompt template voor stap {request.step_code} niet gevonden.")

    ai_response = await ai_service.test_task(
        prompt_template=prompt.prompt_text, 
        input_context=request.input_context
    )

    # Opslaan via de CRUD-laag
    nieuwe_task = crud_tasks.create_task_log(
        db=db,
        dossier_id=request.dossier_id,
        used_prompt=prompt.prompt_text,
        prompt_version=prompt.id,
        input_context=request.input_context,
        output_text=ai_response
    )

    return nieuwe_task


@router.post("/ai8d", status_code=status.HTTP_202_ACCEPTED, response_model=TaskResponse)
async def gen_test_8d(request: TaskBase):
    """
    Ontvangt een generatie verzoek van de monoliet, start de achtergrondtaak en geeft 202 Accepted terug.
    """
    db = None
    try:
        db = SessionLocal()
    except Exception as e:
        print(f"[BackgroundWorker] Kon geen DB verbinding maken: {e}")
        db = None
    
    bruh = await ai_service.test_task(
            dossier_id=request.dossier_id,
            acht_d_stap=request.acht_d_stap,
            dossier_context=request.dossier_context or "",
            db=db,
            nc_excerpt=request.nc_excerpt,
            nc_description=request.nc_description,
            nc_location=request.nc_location,
            nc_comments=request.nc_comments,
            current_analysis=request.current_analysis,
            previous_steps=request.previous_steps
        )

    return TaskResponse(
        status="accepted",
        message=bruh,
        dossier_id=request.dossier_id,
        acht_d_stap=request.step_key
    )

@router.get("/tasks", response_model=List[TaskResponse])
async def gen_get(db: Session = Depends(get_db)):
    tasks = crud_tasks.get_all_tasks(db)
    return tasks
