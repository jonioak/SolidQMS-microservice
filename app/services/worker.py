from uuid import UUID
from datetime import datetime, timezone
from typing import Optional

from app.interfaces.repositories import ITaskRepository, IPromptRepository
from app.interfaces.ai_provider import BaseAIProvider
from app.services.prompt_formatter import PromptFormatterService
from app.schemas.task_schema import TaskUpdate


class TaskProcessor:

    def __init__(
        self,
        task_repo: ITaskRepository,
        prompt_repo: IPromptRepository,
        ai_provider: BaseAIProvider,
        formatter: Optional[PromptFormatterService] = None
    ):
        self.task_repo = task_repo
        self.prompt_repo = prompt_repo
        self.ai_provider = ai_provider
        self.formatter = formatter or PromptFormatterService()

    async def process_task(self, task_id: UUID) -> None:

        task = self.task_repo.get_by_id(task_id)
        if not task:
            return

        prompt_template = self.prompt_repo.get_active_by_type(task.task_type)
        if not prompt_template:
            error_update = TaskUpdate(
                status="failed",
                error_message=f"Geen actieve prompt gevonden voor type {task.task_type}"
            )
            self.task_repo.update_status(task_id, error_update)
            return

        try:
            formatted_prompt = self.formatter.format_prompt(
                template_text=prompt_template.prompt_text,
                input_context=task.input_context or {}
            )
        except KeyError as e:
            error_update = TaskUpdate(
                status="failed",
                error_message=f"Ontbrekende variabele in input_context: {str(e)}"
            )
            self.task_repo.update_status(task_id, error_update)
            return

        ai_response = await self.ai_provider.generate_response(prompt_text=formatted_prompt)

        update_data = TaskUpdate(
            status=ai_response.status,
            output_text=ai_response.output_text,
            input_token_count=ai_response.input_token_count,
            output_token_count=ai_response.output_token_count,
            model_version=ai_response.model_version,
            generation_duration=ai_response.generation_duration,
            error_message=ai_response.error_message,
            used_prompt=formatted_prompt,
            prompt_version=prompt_template.version,
            completed_at=datetime.now(timezone.utc)
        )

        self.task_repo.update_status(task_id, update_data)