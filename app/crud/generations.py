from sqlalchemy.orm import Session
from app.models.generation import Generation

# Create

def create_generation_log(db: Session, dossier_id: int, prompt_title: str, prompt_text: str, input_context: dict, output_text: str):
    """
    Slaat een complete snapshot op van een AI aanroep inclusief de context.
    """
    nieuwe_generatie = Generation(
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

def get_generation_by_id(db: Session, generation_id: int):
    """
    Haalt de details van één specifieke AI-generatie op.
    """
    return db.query(Generation).filter(Generation.id == generation_id).first()

def get_generations_by_dossier(db: Session, dossier_id: int, skip: int = 0, limit: int = 100):
    """
    Haalt de complete AI-historie van één specifiek 8D-dossier op.
    """
    return db.query(Generation)\
             .filter(Generation.dossier_id == dossier_id)\
             .order_by(Generation.created_at.desc())\
             .offset(skip).limit(limit).all()

def get_all_generations(db: Session):
    """
    Voor een admin-dashboard: laat alle AI-activiteit van de hele applicatie zien.
    """
    return db.query(Generation).order_by(Generation.created_at.desc()).all()

# Update

# Delete

