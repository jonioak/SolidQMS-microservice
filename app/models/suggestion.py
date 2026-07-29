from pydantic import BaseModel, Field
from typing import Optional, List

class Suggestion(BaseModel):
    dossier_id: int
    acht_d_stap: str
    content: str = Field(..., description="De door AI gegenereerde advies/voorstel tekst")
    bullet_points: List[str] = Field(default_factory=list, description="Belangrijkste actiepunten of conclusies")
    confidence_score: Optional[float] = Field(None, description="Vertrouwensscore van de generatie")
