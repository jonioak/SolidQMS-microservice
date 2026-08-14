from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List
from datetime import datetime

class GenerationRequest(BaseModel):
    dossier_id: int = Field(..., description="ID van het kwaliteitsdossier")
    acht_d_stap: Optional[str] = Field(None, description="Optionele 8D stap code (bijv. D2, D3, D4, etc.)")
    suggestion_type: Optional[str] = Field(None, description="Optionele monoliet type sleutel (bijv. problem_analysis, root_cause, risk_assessment)")
    dossier_context: Optional[str] = Field("", description="Inhoud en context van het kwaliteitsdossier")
    callback_url: str = Field(..., description="URL waar de AI response naar ge-webhooked moet worden")

    # Optionele monoliet non-conformity velden
    nc_excerpt: Optional[str] = Field(None, description="Non-conformity samenvatting")
    nc_description: Optional[str] = Field(None, description="Volledige NC beschrijving")
    nc_location: Optional[str] = Field(None, description="Locatie van de NC")
    nc_comments: Optional[str] = Field(None, description="Aanvullende opmerkingen bij NC")
    current_analysis: Optional[str] = Field(None, description="Beschrijving van huidige 8D analyse")
    previous_steps: Optional[str] = Field(None, description="Samenvatting van voltooide eerdere 8D stappen")

    @property
    def step_key(self) -> str:
        """Bepaalt de te gebruiken prompt sleutel uit suggestion_type of acht_d_stap"""
        return self.suggestion_type or self.acht_d_stap or "problem_analysis"

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