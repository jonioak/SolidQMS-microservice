from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field
from typing import List, Optional


class PromptBase(BaseModel):
    task_type: str
    prompt_text: str
    input_variables: Optional[List[str]] = None
    change_note: Optional[str] = None

class PromptCreate(PromptBase):
    pass

class PromptUpdate(PromptBase):
    task_type: Optional[str] = None
    prompt_text: Optional[str] = None
    input_variables: Optional[List[str]] = None
    change_note: Optional[str] = None
    is_active: Optional[bool] = None

class PromptResponse(PromptBase):
    id: UUID
    version: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

