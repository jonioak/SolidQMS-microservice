from fastapi import APIRouter, BackgroundTasks, status, Depends

from app.db.database import SessionLocal

from app.schemas.generation import GenerationRequest, GenerationResponse, WebhookPayload, GenerationTest, SuggestionResponse
from app.services.ai_client import AIService
from app.services.webhook import WebhookService

from typing import List, Dict, Any

from sqlalchemy.orm import Session
from app.db.database import get_db
import app.crud.generations as crud

router = APIRouter(prefix="/api/v1", tags=["Generations"])
ai_service = AIService()


@router.post("/ai8d", status_code=status.HTTP_202_ACCEPTED, response_model=GenerationResponse)
async def gen_test_8d(request: GenerationRequest):
    """
    Ontvangt een generatie verzoek van de monoliet, start de achtergrondtaak en geeft 202 Accepted terug.
    """
    db = None
    try:
        db = SessionLocal()
    except Exception as e:
        print(f"[BackgroundWorker] Kon geen DB verbinding maken: {e}")
        db = None
    
    bruh = await ai_service.generation8d(
            dossier_id=request.dossier_id,
            acht_d_stap=request.acht_d_stap,
            dossier_context=request.dossier_context or "",
            db=db,
            nc_excerpt=request.nc_excerpt,
            nc_description=request.nc_description,
            nc_location=request.nc_location,
            nc_comments=request.nc_comments,
            current_analysis=request.current_analysis,
            previous_steps=request.previous_steps
        )

    return GenerationResponse(
        status="accepted",
        message=bruh,
        dossier_id=request.dossier_id,
        acht_d_stap=request.step_key
    )

@router.get("/generations", response_model=List[SuggestionResponse])
async def gen_get(db: Session = Depends(get_db)):
    generations = crud.get_all_generations(db)
    return generations
