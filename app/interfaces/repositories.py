from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.models.prompt import PromptTemplate
from app.models.task import Task
from app.schemas.prompt_schema import PromptCreate, PromptUpdate
from app.schemas.task_schema import TaskCreate, TaskUpdate


class ITaskRepository(ABC):

    @abstractmethod
    def create(self, task_data: TaskCreate) -> Task:
        pass

    @abstractmethod
    def get_by_id(self, task_id: UUID) -> Optional[Task]:
        pass

    @abstractmethod
    def get_by_tenant(self, tenant_id: str, skip: int = 0, limit: int = 100) -> List[Task]:
        pass

    @abstractmethod
    def get_by_type(self, task_type: str, skip: int = 0, limit: int = 100) -> List[Task]:
        pass

    @abstractmethod
    def get_all(self) -> List[Task]:
        pass

    @abstractmethod
    def update_status(self, task_id: UUID, update_data: TaskUpdate) -> Optional[Task]:
        pass


class IPromptRepository(ABC):

    @abstractmethod
    def get_by_id(self, prompt_id: UUID) -> Optional[PromptTemplate]:
        pass

    @abstractmethod
    def get_by_type(self, task_type: str) -> Optional[PromptTemplate]:
        pass

    @abstractmethod
    def get_active_by_type(self, task_type: str) -> Optional[PromptTemplate]:
        pass

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[PromptTemplate]:
        pass

    @abstractmethod
    def create(self, task_type: str, prompt_create: PromptCreate) -> PromptTemplate:
        pass

    @abstractmethod
    def update(self, task_type: str, prompt_update: PromptUpdate) -> Optional[PromptTemplate]:
        pass

    @abstractmethod
    def delete(self, prompt_id: UUID) -> Optional[PromptTemplate]:
        pass
