from sqlalchemy import Column, Integer, String, Text, JSON, DateTime
from datetime import datetime
from app.db.database import Base


class Generation(Base):
    __tablename__ = "generations"

    id = Column(Integer, primary_key=True, index=True)

    dossier_id = Column(Integer, index=True, nullable=False)

    prompt_title = Column(String(100), index=True, nullable=False)
    prompt_text = Column(Text, nullable=False)

    input_context = Column(JSON, nullable=False)

    output_text = Column(Text, nullable=False)    

    created_at = Column(DateTime, default=datetime.utcnow)
