from pydantic import BaseModel, Field
from typing import Optional

class PromptBase(BaseModel):
    step_code: Optional[str] = Field(default="", description="De 8D stap code of sleutel")
    title: Optional[str] = Field(default="", description="Titel van de 8D stap")
    description: Optional[str] = Field(default="", description="Beschrijving en doel van de stap")
    system_prompt: Optional[str] = Field(default="", description="Systeemprompt voor de AI")
    is_active: Optional[bool] = Field(default=True, description="Staat de prompt 'aan' of 'uit'?")

class PromptCreate(PromptBase):
    pass

class PromptUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Bijgewerkte titel van de 8D stap")
    description: Optional[str] = Field(None, description="Bijgewerkte beschrijving")
    system_prompt: Optional[str] = Field(None, description="Bijgewerkte systeemprompt")
    is_active: Optional[bool] = Field(None, description="Staat deze prompt aan of uit?")

class PromptResponse(PromptBase):
    pass
