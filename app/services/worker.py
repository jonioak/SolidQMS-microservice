from uuid import UUID
from datetime import datetime
from app.db.database import SessionLocal
from app.crud import tasks as crud_tasks
from app.crud import prompts as crud_prompts
from app.schemas.task_schema import TaskUpdate
from app.services.ai_client import ai_client

async def process_ai_task(task_id: UUID):
    """
    Deze functie draait op de achtergrond. Hij haalt de juiste prompt op, vult de variabelen in, roept de AI aan en updatet de database.
    """

    db = SessionLocal()
    
    try:
        task = crud_tasks.get_task_by_id(db, task_id)
        if not task:
            return

        # Haal de actieve prompt template op voor dit specifieke task_type
        prompt_template = crud_prompts.get_active_prompt_by_type(db, task.task_type)

        if not prompt_template:
            error_update = TaskUpdate(status="failed", error_message=f"Geen actieve prompt gevonden voor type {task.task_type}")
            crud_tasks.update_task_status(db, task_id, error_update)
            return

        # Vul de variabelen uit de monoliet in de prompt template
        try:
            formatted_prompt = prompt_template.prompt_text.format(**task.input_context)
        except KeyError as e:
            error_update = TaskUpdate(status="failed", error_message=f"Ontbrekende variabele in input_context: {str(e)}")
            crud_tasks.update_task_status(db, task_id, error_update)
            return

        # Roep de asynchrone AI Client aan (hier wacht het proces even)
        ai_result_dict = await ai_client.generate_ai_response(prompt_text=formatted_prompt)

        # Database update
        update_data = TaskUpdate(**ai_result_dict)
        update_data.used_prompt = formatted_prompt
        update_data.prompt_version = prompt_template.version
        update_data.completed_at = datetime.utcnow()

        crud_tasks.update_task_status(db, task_id, update_data)

    finally:
        db.close()