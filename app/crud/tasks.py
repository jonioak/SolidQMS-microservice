from typing import List, Optional

from uuid import UUID
from app.schemas.task_schema import TaskCreate, TaskUpdate
from sqlalchemy.orm import Session
from app.models.task import Task

# Create

def create_task(db: Session, task_data: TaskCreate) -> Task:
    """Wordt aangeroepen door de Ruby monoliet. Zet de taak direct op 'pending'."""
    db_task = Task(
        task_type=task_data.task_type,
        tenant_id=task_data.tenant_id,
        input_context=task_data.input_context,
        status="pending"
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

# Read

def get_task_by_id(db: Session, task_id: UUID) -> Optional[Task]:
    return db.query(Task).filter(Task.id == task_id).first()

def get_tasks_by_tenant(db: Session, tenant_id: str, skip: int = 0, limit: int = 100) -> List[Task]:
    """Haalt taken op per tenant, gesorteerd op nieuwste eerst (handig voor het Ruby QMS dashboard)."""
    return db.query(Task).filter(
        Task.tenant_id == tenant_id
    ).order_by(Task.created_at.desc()).offset(skip).limit(limit).all()

def get_tasks_by_type(db: Session, task_type: str, skip: int = 0, limit: int = 100) -> List[Task]:
    """
    Haalt taken op op basis van hun type.
    """
    return db.query(Task)\
             .filter(Task.task_type == task_type)\
             .order_by(Task.created_at.desc())\
             .offset(skip).limit(limit).all()

def get_all_tasks(db: Session) -> List[Task]:
    """
    Voor een admin-dashboard: laat alle AI-activiteit van de hele applicatie zien.
    """
    return db.query(Task).order_by(Task.created_at.desc()).all()

# Update

def update_task_status(db: Session, task_id: UUID, update_data: TaskUpdate) -> Optional[Task]:
    # 1. Zoek de taak
    db_task = get_task_by_id(db, task_id)
    if not db_task:
        return None
        
    # 2. Loop door ALLE velden in het TaskUpdate object heen (status, output_text, duration_ms, etc.)
    # De .model_dump(exclude_unset=True) zorgt ervoor dat we een dictionary krijgen van alleen de ingevulde velden
    update_dict = update_data.model_dump(exclude_unset=True)
    
    for key, value in update_dict.items():
        # Hiermee doen we dynamisch: db_task.status = "failed", db_task.output_text = "...", etc.
        setattr(db_task, key, value)
        
    # 3. Sla de afzonderlijke velden op in de database
    db.commit()
    db.refresh(db_task)
    return db_task

# Delete

