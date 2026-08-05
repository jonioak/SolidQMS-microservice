from sqlalchemy import Column, Integer, String, Text, Float, DateTime
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List
from app.db.database import Base
from app.schemas.generation import SuggestionBase

# Database SQLAlchemy model voor het opslaan van AI suggesties/generaties
class Suggestion(Base):
    __tablename__ = "suggestions"

    id = Column(Integer, primary_key=True, index=True)
    dossier_id = Column(Integer, index=True)
    acht_d_stap = Column(String, index=True)
    content = Column(Text)
    confidence_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    @classmethod
    def save_suggestion(cls, db: Session, suggestion_data: SuggestionBase) -> Optional["Suggestion"]:
        """Slaat een gegenereerde AI suggestie op in de database"""
        try:
            db_obj = cls(
                dossier_id=suggestion_data.dossier_id,
                acht_d_stap=suggestion_data.acht_d_stap,
                content=suggestion_data.content,
                confidence_score=suggestion_data.confidence_score,
                created_at=suggestion_data.created_at or datetime.utcnow()
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception as e:
            print(f"[SuggestionModel] Fout bij opslaan in DB: {e}")
            db.rollback()
            return None

    @classmethod
    def get_by_dossier(cls, db: Session, dossier_id: int) -> List["Suggestion"]:
        """Haalt alle opgeslagen suggesties op voor een specifiek kwaliteitsdossier"""
        try:
            return db.query(cls).filter(cls.dossier_id == dossier_id).all()
        except Exception as e:
            print(f"[SuggestionModel] Fout bij ophalen voor dossier {dossier_id}: {e}")
            return []

# Re-export SuggestionBase als SuggestionSchema voor backwards-compatibility
SuggestionSchema = SuggestionBase
