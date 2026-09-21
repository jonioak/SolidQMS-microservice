from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional, Any, Dict, List
from datetime import datetime

# class taskRequest(BaseModel):
#     dossier_id: int = Field(..., description="ID van het kwaliteitsdossier")
#     acht_d_stap: Optional[str] = Field(None, description="Optionele 8D stap code (bijv. D2, D3, D4, etc.)")
#     suggestion_type: Optional[str] = Field(None, description="Optionele monoliet type sleutel (bijv. problem_analysis, root_cause, risk_assessment)")
#     dossier_context: Optional[str] = Field("", description="Inhoud en context van het kwaliteitsdossier")
#     callback_url: str = Field(..., description="URL waar de AI response naar ge-webhooked moet worden")

#     nc_excerpt: Optional[str] = Field(None, description="Non-conformity samenvatting")
#     nc_description: Optional[str] = Field(None, description="Volledige NC beschrijving")
#     nc_location: Optional[str] = Field(None, description="Locatie van de NC")
#     nc_comments: Optional[str] = Field(None, description="Aanvullende opmerkingen bij NC")
#     current_analysis: Optional[str] = Field(None, description="Beschrijving van huidige 8D analyse")
#     previous_steps: Optional[str] = Field(None, description="Samenvatting van voltooide eerdere 8D stappen")

#     @property
#     def step_key(self) -> str:
#         """Bepaalt de te gebruiken prompt sleutel uit suggestion_type of acht_d_stap"""
#         return self.suggestion_type or self.acht_d_stap or "problem_analysis"

# class TaskRequest(BaseModel):
#     task_type: str = Field(..., description="De 8D-stap of specifieke prompt, bijv. 'nc_intake_triage'")
#     tenant_id: str = Field(..., description="Unieke identifier van de klant voor datascheiding en billing")
#     input_context: Dict[str, Any] = Field(..., description="De dynamische dossierdata om de prompt placeholders te vullen")

class TaskBase(BaseModel):
    task_type: str
    tenant_id: str
    input_context: Dict[str, Any]

# 2. De Create: Erft alles van Base. Soms voeg je hier extra creatie-specifieke velden toe, 
class TaskCreate(TaskBase):
    pass

# 3. De Response: Erft alles van Base, en voegt velden toe die de database genereert.
class TaskResponse(TaskBase):
    id: UUID
    status: str
    output_text: Optional[str] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

# 4. Intern schema: wordt gebruikt door de background worker om de database bij te werken na een succesvolle of gefaalde AI-generatie.
class TaskUpdate(BaseModel):
    status: str
    output_text: Optional[str] = None
    input_token_count: Optional[int] = None
    output_token_count: Optional[int] = None
    model_version: Optional[str] = None
    generation_duration: Optional[int] = None
    error_message: Optional[str] = None
    completed_at: Optional[datetime] = None # Optioneel: kun je door de worker laten invullen
