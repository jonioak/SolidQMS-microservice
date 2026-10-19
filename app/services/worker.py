from uuid import UUID
from datetime import datetime
from typing import Optional
from app.db.database import SessionLocal
from app.crud import tasks as crud_tasks
from app.crud import prompts as crud_prompts
from app.schemas.task_schema import TaskUpdate
from app.interfaces.ai_provider import BaseAIProvider
from app.services.ai_client import ai_client
from app.services.prompt_formatter import PromptFormatterService

prompt_formatter = PromptFormatterService()


async def process_ai_task(task_id: UUID, ai_provider: Optional[BaseAIProvider] = None):
    """
    Deze functie draait op de achtergrond. Hij haalt de juiste prompt op, vult de variabelen in
    via de PromptFormatterService (SRP), roept de AI provider aan via het BaseAIProvider contract
    (Liskov Substitution Principle), en updatet de database.
    """

    db = SessionLocal()
    
    try:
        task = crud_tasks.get_task_by_id(db, task_id)
        if not task:
            return

        # Haal de actieve prompt template op voor dit specifieke task_type
        prompt_template = crud_prompts.get_active_prompt_by_type(db, task.task_type)

        if not prompt_template:
            error_update = TaskUpdate(
                status="failed",
                error_message=f"Geen actieve prompt gevonden voor type {task.task_type}"
            )
            crud_tasks.update_task_status(db, task_id, error_update)
            return

        # Delegeer prompt formattering aan de PromptFormatterService (Single Responsibility Principle)
        try:
            formatted_prompt = prompt_formatter.format_prompt(
                template_text=prompt_template.prompt_text,
                input_context=task.input_context or {}
            )
        except KeyError as e:
            error_update = TaskUpdate(
                status="failed",
                error_message=f"Ontbrekende variabele in input_context: {str(e)}"
            )
            crud_tasks.update_task_status(db, task_id, error_update)
            return

        # Roep de AI provider aan (Liskov Substitution: MockAIProvider en AnthropicAIProvider zijn 100% uitwisselbaar)
        provider = ai_provider or ai_client
        ai_response = await provider.generate_response(prompt_text=formatted_prompt)

        # Database update
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
            completed_at=datetime.utcnow()
        )

        crud_tasks.update_task_status(db, task_id, update_data)

    finally:
        db.close()