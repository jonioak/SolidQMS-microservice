from datetime import datetime
import uuid

from sqlalchemy import JSON, Column, DateTime, Integer, String, Boolean, Text, func
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import UUID

from typing import Dict, List, Optional
from app.db.database import Base
from app.schemas.prompt_schema import PromptBase

# Database SQLAlchemy Model voor PostgreSQL
class PromptTemplate(Base):
    __tablename__ = "prompt_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    task_type = Column(String(30), nullable=False)  

    version = Column(Integer, nullable=False)  # Versienummer van de prompt

    prompt_text = Column(Text, nullable=False)  # De daadwerkelijke AI prompt tekst

    version = Column(Integer, nullable=False)   # Versienummer van de prompt

    is_active = Column(Boolean, default=True)   # Of de prompt actief is of niet

    input_variables = Column(JSON, nullable=True)  # JSON string van de input variabelen

    change_note = Column(Text, nullable=True)  # Notitie over de wijziging

    created_at = Column(DateTime, default=datetime.utcnow)  # Timestamp van creatie

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Timestamp van laatste update
