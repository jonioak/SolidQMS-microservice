# Bestand: app/crud/prompts.py
from sqlalchemy.orm import Session
from app.models.prompt import PromptTemplate

# Create

def create_prompt(db: Session, title: str, template_text: str, description: str = None):
    """Maakt een nieuwe lege prompt template aan in de database."""
    nieuwe_prompt = PromptTemplate(
        title=title,
        system_prompt=template_text,
        description=description,
        is_active=True
    )
    db.add(nieuwe_prompt)
    db.commit()
    db.refresh(nieuwe_prompt)
    return nieuwe_prompt

# Read

def get_prompt_by_id(db: Session, prompt_id: int):
    """Haalt één specifieke prompt op basis van het database ID."""
    return db.query(PromptTemplate).filter(PromptTemplate.id == prompt_id).first()

def get_prompt_by_step(db: Session, step_code: str):
    """Haalt één specifieke prompt op basis van het step_code/sleutel."""
    return db.query(PromptTemplate).filter(PromptTemplate.step_code == step_code).first()

def get_prompt_by_name(db: Session, prompt_name: str):
    """Haalt één specifieke prompt op basis van de naam."""
    return db.query(PromptTemplate).filter(PromptTemplate.title == prompt_name).first()

def get_all_prompts(db: Session, skip: int = 0, limit: int = 100):
    """Haalt een lijst op van alle prompts (met optie voor paginatie)."""
    return db.query(PromptTemplate).offset(skip).limit(limit).all()

# Update

def update_prompt(db: Session, step_code: str, title: str = None, is_active: bool = None, description: str = None, system_prompt: str = None):
    """
    Past een bestaande prompt aan.
    """
    db_prompt = get_prompt_by_step(db, step_code)
    
    if not db_prompt:
        return None
    if title is not None:
        db_prompt.title = title
    if system_prompt is not None:
        db_prompt.system_prompt = system_prompt
    if is_active is not None:
        db_prompt.is_active = is_active
    if description is not None:
        db_prompt.description = description

    db.commit()
    db.refresh(db_prompt)
    return db_prompt

# Delete

def delete_prompt(db: Session, prompt_id: int):
    """Verwijdert een prompt volledig uit de database."""
    db_prompt = get_prompt_by_id(db, prompt_id)
    
    if db_prompt:
        db.delete(db_prompt)
        db.commit()
    
    return db_prompt