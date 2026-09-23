from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional, Any, Dict, List
from datetime import datetime


class TaskBase(BaseModel):
    task_type: str
    tenant_id: str
    input_context: Dict[str, Any]

class TaskCreate(TaskBase):
    pass

class TaskResponse(TaskBase):
    id: UUID
    status: str
    output_text: Optional[str] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

class TaskUpdate(BaseModel):
    status: str
    output_text: Optional[str] = None
    input_token_count: Optional[int] = None
    output_token_count: Optional[int] = None
    model_version: Optional[str] = None
    generation_duration: Optional[int] = None
    error_message: Optional[str] = None
    completed_at: Optional[datetime] = None 

    used_prompt: Optional[str] = None
    prompt_version: Optional[int] = None
