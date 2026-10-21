from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.interfaces.repositories import ITaskRepository
from app.models.task import Task
from app.schemas.task_schema import TaskCreate, TaskUpdate


class SQLAlchemyTaskRepository(ITaskRepository):

    def __init__(self, db: Session):
        self.db = db

    def create(self, task_data: TaskCreate) -> Task:
        db_task = Task(
            task_type=task_data.task_type,
            tenant_id=task_data.tenant_id,
            input_context=task_data.input_context,
            status="pending"
        )
        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)
        return db_task

    def get_by_id(self, task_id: UUID) -> Optional[Task]:
        return self.db.query(Task).filter(Task.id == task_id).first()

    def get_by_tenant(self, tenant_id: str, skip: int = 0, limit: int = 100) -> List[Task]:
        return self.db.query(Task).filter(
            Task.tenant_id == tenant_id
        ).order_by(Task.created_at.desc()).offset(skip).limit(limit).all()

    def get_by_type(self, task_type: str, skip: int = 0, limit: int = 100) -> List[Task]:
        return self.db.query(Task).filter(
            Task.task_type == task_type
        ).order_by(Task.created_at.desc()).offset(skip).limit(limit).all()

    def get_all(self) -> List[Task]:
        return self.db.query(Task).order_by(Task.created_at.desc()).all()

    def update_status(self, task_id: UUID, update_data: TaskUpdate) -> Optional[Task]:
        update_dict = update_data.model_dump(exclude_unset=True)
        rows_affected = self.db.query(Task).filter(Task.id == task_id).update(update_dict)

        if rows_affected == 0:
            return None

        self.db.commit()
        return self.get_by_id(task_id)
