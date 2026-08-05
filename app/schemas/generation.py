from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List
from datetime import datetime

class GenerationRequest(BaseModel):
    dossier_id: int = Field(..., description="ID van het kwaliteitsdossier")
    acht_d_stap: str = Field(..., description="De 8D stap (bijv. D1, D2, D3, D4, D5, D6, D7, D8)")
    dossier_context: str = Field(..., description="Inhoud en context van het kwaliteitsdossier")
    callback_url: str = Field(..., description="URL waar de AI response naar ge-webhooked moet worden")

class GenerationResponse(BaseModel):
    status: str = Field("accepted", description="Status van het verzoek")
    message: str = Field("Generatie is gestart op de achtergrond", description="Bericht voor de client")
    dossier_id: int
    acht_d_stap: str

class SuggestionBase(BaseModel):
    dossier_id: int
    acht_d_stap: str
    content: str = Field(..., description="De door AI gegenereerde advies/voorstel tekst")
    bullet_points: List[str] = Field(default_factory=list, description="Belangrijkste actiepunten of conclusies")
    confidence_score: Optional[float] = Field(None, description="Vertrouwensscore van de generatie")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Tijdstip van generatie")


class WebhookPayload(BaseModel):
    dossier_id: int
    acht_d_stap: str
    status: str  # "completed" of "failed"
    suggestion: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class GenerationTest(BaseModel):
    prompt: str = Field(..., description="De instructie voor de AI")

class GenerationTeestResponse(BaseModel):
    response: str = Field(..., description="Antwoord van de AI")