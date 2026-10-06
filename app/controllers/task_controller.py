from fastapi import APIRouter, BackgroundTasks, status, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.schemas.task_schema import TaskResponse, TaskCreate, TaskQueuedResponse
from app.services.ai_client import AIService
from app.services.worker import process_ai_task
from app.db.database import get_db

import app.crud.tasks as crud_tasks

router = APIRouter(prefix="/tasks", tags=["Tasks"])
ai_service = AIService()


@router.post("/create", response_model=TaskQueuedResponse, status_code=status.HTTP_201_CREATED)
def create_new_task(task_data: TaskCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Ontvangt een nieuwe taak vanuit de QMS monoliet.
    Zet de taak direct op status 'pending' en start de AI-generatie op de achtergrond.
    """

    db_task = crud_tasks.create_task(db=db, task_data=task_data)
    
    background_tasks.add_task(process_ai_task, db_task.id)
    
    # Stuurt "pending" terug naar de monoliet zodat deze kan wachten op de AI response
    return {
        "id": db_task.id,
        "status": db_task.status,
        "message": "Taak is in de wachtrij gezet."
    }


@router.get("/", response_model=List[TaskResponse])
async def get_tasks(db: Session = Depends(get_db)):
    tasks = crud_tasks.get_all_tasks(db)
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
def get_task_status(task_id: UUID, db: Session = Depends(get_db)):
    """
    Ruby roept dit endpoint elke X seconden aan om te kijken of Claude al klaar is.
    """
    task = crud_tasks.get_task_by_id(db=db, task_id=task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Taak met ID {task_id} bestaat niet."
        )
        
    # Geeft de huidige staat terug (bijv: status="pending" of status="completed" met output_text)
    return task