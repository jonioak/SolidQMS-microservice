from sqlalchemy import Column, Integer, String, Boolean, Text
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from app.db.database import Base
from app.schemas.prompt import PromptBase

# Database SQLAlchemy Model voor PostgreSQL
class PromptTemplate(Base):
    __tablename__ = "prompt_templates"

    id = Column(Integer, primary_key=True, index=True)
    step_code = Column(String, unique=True, index=True) # Bijv: "D1", "D2", etc.
    title = Column(String)                              # Bijv: "Team Samenstellen"
    description = Column(Text)                         # Bijv: "Stel een multidisciplinair team samen..."
    system_prompt = Column(Text)                       # De daadwerkelijke AI prompt tekst
    is_active = Column(Boolean, default=True)          # Staat deze prompt 'aan' of 'uit'?

    @classmethod
    def get_all_prompts(cls, db: Session) -> List[PromptBase]:
        """
        Haalt alle prompts op uit de PostgreSQL database.
        Indien de database leeg is, worden de standaard 8D-prompts automatisch ge-seed in de DB.
        """
        try:
            db_prompts = db.query(cls).all()
            if not db_prompts:
                # Auto-seed in database indien de tabel leeg is
                cls._seed_database(db)
                db_prompts = db.query(cls).all()

            if db_prompts:
                return [
                    PromptBase(
                        step_code=p.step_code,
                        title=p.title,
                        description=p.description,
                        system_prompt=p.system_prompt
                    )
                    for p in db_prompts
                ]
        except Exception as e:
            print(f"[PromptModel] Fout bij ophalen uit DB (Fallback in-memory): {e}")

        # Nood-fallback alleen als de DB verbinding mislukt
        return list(DEFAULT_8D_PROMPTS.values())

    @classmethod
    def get_by_step(cls, db: Session, step_code: str) -> Optional[PromptBase]:
        """
        Haalt een specifieke prompt op uit de PostgreSQL database.
        """
        step = step_code.upper()
        try:
            p = db.query(cls).filter(cls.step_code == step).first()
            if not p:
                # Als de DB nog leeg was, voer seed uit en probeer opnieuw
                if db.query(cls).count() == 0:
                    cls._seed_database(db)
                    p = db.query(cls).filter(cls.step_code == step).first()

            if p:
                return PromptBase(
                    step_code=p.step_code,
                    title=p.title,
                    description=p.description,
                    system_prompt=p.system_prompt
                )
        except Exception as e:
            print(f"[PromptModel] Fout bij ophalen {step} uit DB: {e}")

        # Nood-fallback alleen als de DB verbinding mislukt
        return DEFAULT_8D_PROMPTS.get(step)

    @classmethod
    def update_prompt(cls, db: Session, step_code: str, title: Optional[str] = None, description: Optional[str] = None, system_prompt: Optional[str] = None) -> Optional[PromptBase]:
        """
        Werkt een prompt rechtstreeks bij in de PostgreSQL database.
        """
        step = step_code.upper()
        try:
            p = db.query(cls).filter(cls.step_code == step).first()
            if not p:
                # Als de tabel nog leeg is, seed de DB eerst
                if db.query(cls).count() == 0:
                    cls._seed_database(db)
                    p = db.query(cls).filter(cls.step_code == step).first()

            if p:
                if title is not None:
                    p.title = title
                if description is not None:
                    p.description = description
                if system_prompt is not None:
                    p.system_prompt = system_prompt
                db.commit()
                db.refresh(p)

                res = PromptBase(
                    step_code=p.step_code,
                    title=p.title,
                    description=p.description,
                    system_prompt=p.system_prompt
                )
                DEFAULT_8D_PROMPTS[step] = res
                return res
        except Exception as e:
            print(f"[PromptModel] Fout bij updaten in DB: {e}")
            db.rollback()

        # Nood-fallback alleen als DB niet bereikbaar is
        if step in DEFAULT_8D_PROMPTS:
            current = DEFAULT_8D_PROMPTS[step]
            updates = {k: v for k, v in {"title": title, "description": description, "system_prompt": system_prompt}.items() if v is not None}
            updated = current.model_copy(update=updates)
            DEFAULT_8D_PROMPTS[step] = updated
            return updated

        return None

    @classmethod
    def _seed_database(cls, db: Session):
        """Hulpfunctie om de PostgreSQL database te vullen met standaard 8D-prompts"""
        try:
            for step_code, item in DEFAULT_8D_PROMPTS.items():
                if not db.query(cls).filter(cls.step_code == step_code).first():
                    db.add(cls(
                        step_code=item.step_code,
                        title=item.title,
                        description=item.description,
                        system_prompt=item.system_prompt,
                        is_active=True
                    ))
            db.commit()
            print("[PromptModel] ✅ Automatisch ge-seed in PostgreSQL database!")
        except Exception as err:
            print(f"[PromptModel] Fout bij auto-seeden DB: {err}")
            db.rollback()


# Standaard 8D Prompts catalogus (gebruikt als noded-fallback)
DEFAULT_8D_PROMPTS: Dict[str, PromptBase] = {
    "D1": PromptBase(
        step_code="D1",
        title="Team Samenstellen",
        description="Stel een multidisciplinair team samen met de nodige product/proceskennis.",
        system_prompt="Je bent een expert in Quality Management Systems (QMS). Help bij het voorstellen van rollen en expertises voor het 8D team op basis van de dossier context."
    ),
    "D2": PromptBase(
        step_code="D2",
        title="Probleem Omschrijving",
        description="Beschrijf het probleem in detail (Wie, Wat, Waar, Wanneer, Waarom, Hoe, Hoeveel).",
        system_prompt="Je bent een QMS expert. Formuleer een heldere, objectieve probleemomschrijving volgens 5W2H op basis van de dossier context."
    ),
    "D3": PromptBase(
        step_code="D3",
        title="Tijdelijke Maatregelen (Containment)",
        description="Definieer en implementeer tijdelijke maatregelen om de klant te beschermen.",
        system_prompt="Je bent een QMS expert. Stel directe, tijdelijke noodmaatregelen voor om verdere uitstroom van afwijkingen te voorkomen."
    ),
    "D4": PromptBase(
        step_code="D4",
        title="Worteloorzaak Analyse (Root Cause)",
        description="Identificeer alle mogelijke oorzaken en bepaal de echte worteloorzaak (5-Why, Ishikawa).",
        system_prompt="Je bent een QMS expert. Voer een grondige 5-Why en root cause analyse uit op basis van de situatie."
    ),
    "D5": PromptBase(
        step_code="D5",
        title="Gekozen Correctieve Maatregelen",
        description="Selecteer de beste definitieve correctieve maatregelen.",
        system_prompt="Je bent een QMS expert. Stel definitieve maatregelen voor die de worteloorzaak permanent wegnemen."
    ),
    "D6": PromptBase(
        step_code="D6",
        title="Implementatie Correctieve Maatregelen",
        description="Implementeer de correctieve maatregelen en borg de werking.",
        system_prompt="Je bent een QMS expert. Maak een implementatieplan en borgingsplan voor de gekozen correctieve acties."
    ),
    "D7": PromptBase(
        step_code="D7",
        title="Preventieve Maatregelen",
        description="Pas systemen, processen en procedures aan om herhaling te voorkomen.",
        system_prompt="Je bent een QMS expert. Stel preventieve maatregelen en procesaanpassingen voor om soortgelijke problemen in de toekomst te voorkomen."
    ),
    "D8": PromptBase(
        step_code="D8",
        title="Team Bedanken & Dossier Sluiten",
        description="Erken de bijdrage van het team en sluit het 8D dossier formeel af.",
        system_prompt="Je bent een QMS expert. Formuleer een formele afsluiting en waardering voor het 8D team."
    )
}