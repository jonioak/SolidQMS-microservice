from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field
from typing import List, Optional


class PromptBase(BaseModel):
    prompt_text: str

class PromptCreate(PromptBase):
    pass

class PromptUpdate(PromptBase):
    change_note: Optional[str] = None

class PromptResponse(PromptBase):
    id: UUID
    task_type: str
    input_variables: Optional[List[str]] = None
    version: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

