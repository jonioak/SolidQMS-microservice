# Bestand: app/crud/prompts.py
from sqlalchemy.orm import Session
from app.models.prompt import PromptTemplate, DEFAULT_8D_PROMPTS

# Lezen

def get_prompt_by_id(db: Session, prompt_id: int):
    """Haalt één specifieke prompt op basis van het database ID."""
    try:
        return db.query(PromptTemplate).filter(PromptTemplate.id == prompt_id).first()
    except Exception:
        return None

def get_prompt_by_step(db: Session, prompt_code: str):
    """Haalt één specifieke prompt op uit DB of fallback in-memory."""
    return PromptTemplate.get_by_step(db, prompt_code)

def get_prompt_by_name(db: Session, prompt_name: str):
    """Haalt één specifieke prompt op basis van de naam."""
    try:
        return db.query(PromptTemplate).filter(PromptTemplate.title == prompt_name).first()
    except Exception:
        return None

def get_all_prompts(db: Session, skip: int = 0, limit: int = 100):
    """Haalt een lijst op van alle prompts (met fallback voor offline DB)."""
    return PromptTemplate.get_all_prompts(db)

# Aanmaken

def create_prompt(db: Session, title: str, template_text: str, description: str = None):
    """Maakt een nieuwe lege prompt template aan in de database."""
    try:
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
    except Exception as e:
        print(f"[CRUD] Fout bij aanmaken prompt: {e}")
        try:
            db.rollback()
        except Exception:
            pass
        return None

# Updaten

def update_prompt(db: Session, step_code: str, template_text: str = None, is_active: bool = None, description: str = None, system_prompt: str = None, title: str = None):
    """
    Past een bestaande prompt aan met in-memory/DB fallback.
    """
    sys_prompt = system_prompt or template_text
    prompt_title = title or (template_text if not system_prompt else None)
    return PromptTemplate.update_prompt(
        db=db,
        step_code=step_code,
        title=prompt_title,
        description=description,
        system_prompt=sys_prompt,
        is_active=is_active
    )

# Verwijderen

def delete_prompt(db: Session, prompt_id: int):
    """Verwijdert een prompt volledig uit de database."""
    try:
        db_prompt = get_prompt_by_id(db, prompt_id)
        if db_prompt:
            db.delete(db_prompt)
            db.commit()
        return db_prompt
    except Exception:
        return None