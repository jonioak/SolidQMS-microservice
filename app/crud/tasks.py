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
    
    # Maak de dictionary met alleen de meegestuurde velden
    update_dict = update_data.model_dump(exclude_unset=True)
    
    # Laat SQLAlchemy direct de update uitvoeren op de database
    rows_affected = db.query(Task).filter(Task.id == task_id).update(update_dict)
    
    # Als er 0 rijen zijn aangepast, bestond de taak niet
    if rows_affected == 0:
        return None
        
    db.commit()
    
    return get_task_by_id(db, task_id)

# Delete

