from sqlalchemy import Column, Integer, String, Boolean, Text, func
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from app.db.database import Base
from app.schemas.prompt import PromptBase

# Database SQLAlchemy Model voor PostgreSQL
class PromptTemplate(Base):
    __tablename__ = "prompt_templates"

    id = Column(Integer, primary_key=True, index=True)
    step_code = Column(String, unique=True, index=True) # Unieke sleutel, bijv: "problem_analysis", "root_cause", "D1", etc.
    title = Column(String)                              # Bijv: "Problem Analysis (D2)"
    description = Column(Text)                         # Bijv: "Generates AI-powered suggestions..."
    system_prompt = Column(Text)                       # De daadwerkelijke AI prompt tekst
    is_active = Column(Boolean, default=True)          # Staat deze prompt 'aan' of 'uit'?