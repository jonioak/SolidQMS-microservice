from fastapi import APIRouter, BackgroundTasks, status, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.schemas.task_schema import TaskResponse, TaskCreate
from app.services.ai_client import AIService
from app.services.worker import process_ai_task
from app.db.database import get_db

import app.crud.tasks as crud_tasks

router = APIRouter(prefix="/tasks", tags=["Tasks"])
ai_service = AIService()


@router.post("/create", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_new_task(task_data: TaskCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Ontvangt een nieuwe taak vanuit de QMS monoliet.
    Zet de taak direct op status 'pending' en start de AI-generatie op de achtergrond.
    """

    db_task = crud_tasks.create_task(db=db, task_data=task_data)
    
    background_tasks.add_task(process_ai_task, db_task.id)
    
    # Stuurt "pending" terug naar de monoliet zodat deze kan wachten op de AI response
    return db_task


@router.get("/", response_model=List[TaskResponse])
async def get_tasks(db: Session = Depends(get_db)):
    tasks = crud_tasks.get_all_tasks(db)
    return tasks
