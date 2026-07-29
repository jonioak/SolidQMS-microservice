from pydantic import BaseModel, Field
from typing import Optional

class PromptBase(BaseModel):
    step_code: str = Field(..., description="De 8D stap code (bijv. D1..D8)")
    title: str = Field(..., description="Titel van de 8D stap")
    description: str = Field(..., description="Beschrijving en doel van de stap")
    system_prompt: str = Field(..., description="Systeemprompt voor de AI")

class PromptCreate(PromptBase):
    pass

class PromptUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Bijgewerkte titel van de 8D stap")
    description: Optional[str] = Field(None, description="Bijgewerkte beschrijving")
    system_prompt: Optional[str] = Field(None, description="Bijgewerkte systeemprompt")

class PromptResponse(PromptBase):
    pass
