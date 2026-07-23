from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="SolidQMS AI Microservice")

# Dit is het 'Contract' (De JSON-velden die we verwachten van de monoliet)
class GenerationRequest(BaseModel):
    dossier_id: int
    acht_d_stap: str
    dossier_context: str
    callback_url: str

# Dit is je GenerationsController (API Receiver)
@app.post("/api/v1/generations", status_code=202)
async def create_generation(request: GenerationRequest):
    # Hier komt straks de logica om de AI aan te roepen (ai_client)
    # Voor nu printen we alleen even wat we binnenkrijgen
    print(f"Taak ontvangen voor dossier: {request.dossier_id}")
    
    return {"status": "accepted", "message": "Generatie is gestart op de achtergrond"}