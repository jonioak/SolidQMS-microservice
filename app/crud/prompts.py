# Bestand: app/crud/prompts.py
from sqlalchemy.orm import Session
from app.models.prompt import PromptTemplate
from app.schemas.prompt_schema import PromptCreate, PromptUpdate
from app.utils.prompt_parser import extract_prompt_variables

# Create

def create_prompt(db: Session, task_type: str, prompt_create: PromptCreate):
    """Maakt een nieuwe lege prompt template aan in de database."""

    nieuwe_prompt = PromptTemplate(
        task_type=task_type,
        prompt_text=prompt_create.prompt_text,
        input_variables=extract_prompt_variables(prompt_create.prompt_text),
        version = 1,
        is_active=True,
    )
    db.add(nieuwe_prompt)
    db.commit()
    db.refresh(nieuwe_prompt)
    return nieuwe_prompt

# Read

def get_prompt_by_id(db: Session, prompt_id: int):
    """Haalt één specifieke prompt op basis van het database ID."""
    return db.query(PromptTemplate).filter(PromptTemplate.id == prompt_id).first()

def get_prompt_by_type(db: Session, task_type: str):
    """Haalt één specifieke prompt op basis van het task_type."""
    return db.query(PromptTemplate).filter(PromptTemplate.task_type == task_type).first()

def get_prompt_by_name(db: Session, prompt_name: str):
    """Haalt één specifieke prompt op basis van de naam."""
    return db.query(PromptTemplate).filter(PromptTemplate.title == prompt_name).first()

def get_all_prompts(db: Session, skip: int = 0, limit: int = 100):
    """Haalt een lijst op van alle prompts (met optie voor paginatie)."""
    return db.query(PromptTemplate).offset(skip).limit(limit).all()

def get_active_prompt_by_type(db: Session, task_type: str):
    """Haalt de actieve prompt op voor een specifiek task_type."""
    return db.query(PromptTemplate).filter(
        PromptTemplate.task_type == task_type,
        PromptTemplate.is_active == True
    ).first()

# Update

def update_prompt(db: Session, 
                  task_type: str, 
                  prompt_update: PromptUpdate):
                  
    """
    Past een bestaande prompt aan.
    """
    old_prompt = get_active_prompt_by_type(db, task_type)
    if not old_prompt:
        return None

    old_prompt.is_active = False

    new_prompt = PromptTemplate(
        task_type=task_type,
        prompt_text=prompt_update.prompt_text,
        input_variables=extract_prompt_variables(prompt_update.prompt_text),
        change_note=prompt_update.change_note,
        is_active=True,
        version=old_prompt.version + 1,
        created_at=old_prompt.created_at
    )

    db.add(new_prompt)
    db.commit()
    db.refresh(new_prompt)
    
    return new_prompt

# Delete

def delete_prompt(db: Session, prompt_id: int):
    """Verwijdert een prompt volledig uit de database."""
    db_prompt = get_prompt_by_id(db, prompt_id)
    
    if db_prompt:
        db.delete(db_prompt)
        db.commit()
    
    return db_prompt