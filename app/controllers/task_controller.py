from fastapi import APIRouter, BackgroundTasks, status, Depends, HTTPException
from typing import List
from uuid import UUID

from app.schemas.task_schema import TaskResponse, TaskCreate, TaskQueuedResponse
from app.services.worker import TaskProcessor
from app.interfaces.repositories import ITaskRepository
from app.dependencies import get_task_repository, get_task_processor

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/create", response_model=TaskQueuedResponse, status_code=status.HTTP_201_CREATED)
def create_new_task(
    task_data: TaskCreate,
    background_tasks: BackgroundTasks,
    task_repo: ITaskRepository = Depends(get_task_repository),
    processor: TaskProcessor = Depends(get_task_processor)
):
    db_task = task_repo.create(task_data=task_data)
    
    background_tasks.add_task(processor.process_task, db_task.id)
    
    # Stuurt "pending" terug naar de monoliet zodat deze kan wachten op de AI response
    return {
        "id": db_task.id,
        "status": db_task.status,
        "message": "Taak is in de wachtrij gezet."
    }


@router.get("/", response_model=List[TaskResponse])
async def get_tasks(task_repo: ITaskRepository = Depends(get_task_repository)):

    return task_repo.get_all()


@router.get("/{task_id}", response_model=TaskResponse)
def get_task_status(
    task_id: UUID,
    task_repo: ITaskRepository = Depends(get_task_repository)
):
    task = task_repo.get_by_id(task_id=task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Taak met ID {task_id} bestaat niet."
        )
        
    return task