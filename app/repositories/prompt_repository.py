from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.interfaces.repositories import IPromptRepository
from app.models.prompt import PromptTemplate
from app.schemas.prompt_schema import PromptCreate, PromptUpdate
from app.utils.prompt_parser import extract_prompt_variables


class SQLAlchemyPromptRepository(IPromptRepository):

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, prompt_id: UUID) -> Optional[PromptTemplate]:
        return self.db.query(PromptTemplate).filter(PromptTemplate.id == prompt_id).first()

    def get_by_type(self, task_type: str) -> Optional[PromptTemplate]:
        return self.db.query(PromptTemplate).filter(PromptTemplate.task_type == task_type).first()

    def get_active_by_type(self, task_type: str) -> Optional[PromptTemplate]:
        return self.db.query(PromptTemplate).filter(
            PromptTemplate.task_type == task_type,
            PromptTemplate.is_active == True
        ).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[PromptTemplate]:
        return self.db.query(PromptTemplate).offset(skip).limit(limit).all()

    def create(self, task_type: str, prompt_create: PromptCreate) -> PromptTemplate:
        nieuwe_prompt = PromptTemplate(
            task_type=task_type,
            prompt_text=prompt_create.prompt_text,
            input_variables=extract_prompt_variables(prompt_create.prompt_text),
            version=1,
            is_active=True,
        )
        self.db.add(nieuwe_prompt)
        self.db.commit()
        self.db.refresh(nieuwe_prompt)
        return nieuwe_prompt

    def update(self, task_type: str, prompt_update: PromptUpdate) -> Optional[PromptTemplate]:
        # Append-only versiebeheer: archiveer de oude actieve versie
        old_prompt = self.get_active_by_type(task_type)
        if not old_prompt:
            return None

        old_prompt.is_active = False

        # Maak een nieuwe versie aan met verhoogd versienummer
        new_prompt = PromptTemplate(
            task_type=task_type,
            prompt_text=prompt_update.prompt_text,
            input_variables=extract_prompt_variables(prompt_update.prompt_text),
            change_note=prompt_update.change_note,
            is_active=True,
            version=old_prompt.version + 1,
            created_at=old_prompt.created_at
        )

        self.db.add(new_prompt)
        self.db.commit()
        self.db.refresh(new_prompt)
        return new_prompt

    def delete(self, prompt_id: UUID) -> Optional[PromptTemplate]:
        db_prompt = self.get_by_id(prompt_id)
        if db_prompt:
            self.db.delete(db_prompt)
            self.db.commit()
        return db_prompt
