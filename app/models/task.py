from sqlite3.dbapi2 import Timestamp
import uuid
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.db.database import Base



class Task(Base):
    __tablename__ = "ai_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    task_type = Column(String(30), nullable=False)

    tenant_id = Column(String(50), nullable=False)

    status = Column(String(30), index=True, nullable=False)

    error_message = Column(Text, nullable=True)

    used_prompt = Column(Text, nullable=True)

    prompt_version = Column(Integer, nullable=True)

    input_context = Column(JSON, nullable=False)

    output_text = Column(Text, nullable=True)    

    created_at = Column(DateTime, default=datetime.utcnow)

    completed_at = Column(DateTime, nullable=True)

    generation_duration = Column(Integer, nullable=True)  # in milliseconds

    model_version = Column(String(50), nullable=True)  # "claude-sonnet-4-6"

    input_token_count = Column(Integer, nullable=True)

    output_token_count = Column(Integer, nullable=True)

    retry_count = Column(Integer, default=0, nullable=False)
