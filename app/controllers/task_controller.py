from fastapi import APIRouter, BackgroundTasks, status, Depends, HTTPException

from app.db.database import SessionLocal

from app.schemas.task_schema import TaskBase, TaskResponse, TaskCreate
from app.services.ai_client import AIService
from app.services.worker import process_ai_task

from typing import List, Dict, Any

from sqlalchemy.orm import Session
from app.db.database import get_db

from app.models.prompt import PromptTemplate

import app.crud.tasks as crud_tasks
import app.crud.prompts as crud_prompts

router = APIRouter(prefix="/api/v1", tags=["tasks"])
ai_service = AIService()


@router.post("/create_task", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_new_task(task_data: TaskCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Ontvangt een nieuwe taak vanuit de QMS monoliet.
    Zet de taak direct op status 'pending' en start de AI-generatie op de achtergrond.
    """
    # 1. Sla de taak op als 'pending'
    db_task = crud_tasks.create_task(db=db, task_data=task_data)
    
    # 2. Vertel FastAPI om de worker op de achtergrond te starten met dit task_id
    background_tasks.add_task(process_ai_task, db_task.id)
    
    # 3. Geef het task_id en de pending status direct terug aan de Ruby monoliet
    return db_task


@router.post("/ai", response_model=TaskResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_ai_suggestion(request: TaskBase, db: Session = Depends(get_db)):

    # Haal de prompt op via de CRUD-laag
    prompt = crud_prompts.get_prompt_by_type(db, task_type=request.task_type)
    
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
