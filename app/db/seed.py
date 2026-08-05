import os
import sys

# Zorg dat de root van het project in sys.path staat
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base
from app.models.prompt import PromptTemplate, DEFAULT_8D_PROMPTS


def seed_standaard_prompts(db: Session):
    """
    Zorgt ervoor dat de 8D prompt templates aanwezig zijn in de PostgreSQL database.
    Controleert per 8D-stap en voegt ontbrekende stappen toe.
    """
    print("🌱 Controleren en seeden van standaard 8D-prompts in database...")
    toegevoegd_aantal = 0
    
    for step_code, item in DEFAULT_8D_PROMPTS.items():
        bestaande_prompt = db.query(PromptTemplate).filter(PromptTemplate.step_code == step_code).first()
        if not bestaande_prompt:
            nieuwe_prompt = PromptTemplate(
                step_code=item.step_code,
                title=item.title,
                description=item.description,
                system_prompt=item.system_prompt,
                is_active=True
            )
            db.add(nieuwe_prompt)
            toegevoegd_aantal += 1
    
    if toegevoegd_aantal > 0:
        db.commit()
        print(f"✅ Seeden voltooid! {toegevoegd_aantal} nieuwe 8D-prompts toegevoegd aan de database.")
    else:
        totaal = db.query(PromptTemplate).count()
        print(f"ℹ️ Alle 8D-prompts zijn al aanwezig in de database (Totaal: {totaal}). Seeden overgeslagen.")


if __name__ == "__main__":
    print("🚀 Handmatige database seed gestart...")
    try:
        Base.metadata.create_all(bind=engine)
        db_session = SessionLocal()
        try:
            seed_standaard_prompts(db_session)
        finally:
            db_session.close()
    except Exception as err:
        print(f"❌ Fout tijdens handmatige seed: {err}")
        sys.exit(1)