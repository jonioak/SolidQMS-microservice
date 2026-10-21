from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.interfaces.repositories import IPromptRepository, ITaskRepository
from app.interfaces.ai_provider import BaseAIProvider
from app.repositories.prompt_repository import SQLAlchemyPromptRepository
from app.repositories.task_repository import SQLAlchemyTaskRepository
from app.services.ai_client import AnthropicAIProvider
from app.services.prompt_formatter import PromptFormatterService
from app.services.worker import TaskProcessor


def get_task_repository(db: Session = Depends(get_db)) -> ITaskRepository:
    return SQLAlchemyTaskRepository(db)


def get_prompt_repository(db: Session = Depends(get_db)) -> IPromptRepository:
    return SQLAlchemyPromptRepository(db)


def get_ai_provider() -> BaseAIProvider:
    return AnthropicAIProvider()


def get_prompt_formatter() -> PromptFormatterService:
    return PromptFormatterService()


def get_task_processor(
    task_repo: ITaskRepository = Depends(get_task_repository),
    prompt_repo: IPromptRepository = Depends(get_prompt_repository),
    ai_provider: BaseAIProvider = Depends(get_ai_provider),
    formatter: PromptFormatterService = Depends(get_prompt_formatter)
) -> TaskProcessor:
    return TaskProcessor(
        task_repo=task_repo,
        prompt_repo=prompt_repo,
        ai_provider=ai_provider,
        formatter=formatter
    )
