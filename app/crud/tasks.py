from sqlalchemy.orm import Session
from app.models.task import Task

# Create

def create_task_log(db: Session, 
                    task_type: str, 
                    tenant_id: str, 
                    used_prompt: str, 
                    prompt_version: int, 
                    input_context: dict, 
                    output_text: str, 
                    input_token_count: int, 
                    output_token_count: int, 
                    model_version: str
                    ):
    """
    Slaat een complete snapshot op van een AI aanroep inclusief de context.
    """
    nieuwe_generatie = Task(
        task_type=task_type,
        tenant_id=tenant_id,
        status="pending",
        used_prompt=used_prompt,
        prompt_version=prompt_version,
        input_context=input_context,
        output_text=output_text,
        input_token_count=input_token_count,
        output_token_count=output_token_count,
        model_version=model_version
    )
    
    db.add(nieuwe_generatie)
    db.commit()
    db.refresh(nieuwe_generatie)
    
    return nieuwe_generatie

def create_task_log_old(db: Session, dossier_id: int, prompt_title: str, prompt_text: str, input_context: dict, output_text: str):
    """
    Slaat een complete snapshot op van een AI aanroep inclusief de context.
    """
    nieuwe_generatie = Task(
        dossier_id=dossier_id,
        prompt_title=prompt_title,
        prompt_text=prompt_text,
        input_context=input_context,
        output_text=output_text
    )
    
    db.add(nieuwe_generatie)
    db.commit()
    db.refresh(nieuwe_generatie)
    
    return nieuwe_generatie

# Read

def get_task_by_id(db: Session, task_id: int):
    """
    Haalt de details van één specifieke AI-taak op.
    """
    return db.query(Task).filter(Task.id == task_id).first()

def get_tasks_by_dossier(db: Session, dossier_id: int, skip: int = 0, limit: int = 100):
    """
    Haalt de complete AI-historie van één specifiek 8D-dossier op.
    """
    return db.query(Task)\
             .filter(Task.dossier_id == dossier_id)\
             .order_by(Task.created_at.desc())\
             .offset(skip).limit(limit).all()

def get_all_tasks(db: Session):
    """
    Voor een admin-dashboard: laat alle AI-activiteit van de hele applicatie zien.
    """
    return db.query(Task).order_by(Task.created_at.desc()).all()

# Update

# Delete

