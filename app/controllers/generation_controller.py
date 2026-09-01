from fastapi import APIRouter, BackgroundTasks, status, Depends, HTTPException

from app.db.database import SessionLocal

from app.schemas.generation import GenerationRequest, SuggestionResponse, WebhookPayload, GenerationTest, SuggestionResponse, GenerateRequest
from app.services.ai_client import AIService
from app.services.webhook import WebhookService

from typing import List, Dict, Any

from sqlalchemy.orm import Session
from app.db.database import get_db

from app.models.prompt import PromptTemplate

import app.crud.generations as crud_generations
import app.crud.prompts as crud_prompts

router = APIRouter(prefix="/api/v1", tags=["Generations"])
ai_service = AIService()

@router.post("/ah", response_model=SuggestionResponse)
async def generate_ai_suggestion(request: GenerateRequest, db: Session = Depends(get_db)):
    # 1. Haal de prompt op via de CRUD-laag
    prompt = crud_prompts.get_prompt_by_step(db, step_code=request.step_code)
    
    if not prompt:
        raise HTTPException(status_code=404, detail=f"Prompt template voor stap {request.step_code} niet gevonden.")

    # 2. AI generatie (Placeholder)
    ai_response = await ai_service.test_generation(
        prompt_template=prompt.system_prompt, 
        input_context=request.input_context
    )

    # 3. Opslaan via de CRUD-laag
    nieuwe_generation = crud_generations.create_generation_log(
        db=db,
        dossier_id=request.dossier_id,
        prompt_title=prompt.title,
        prompt_text=prompt.system_prompt,
        input_context=request.input_context,
        output_text=ai_response
    )

    return nieuwe_generation


@router.post("/ai8d", status_code=status.HTTP_202_ACCEPTED, response_model=SuggestionResponse)
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
    
    bruh = await ai_service.test_generation(
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

    return SuggestionResponse(
        status="accepted",
        message=bruh,
        dossier_id=request.dossier_id,
        acht_d_stap=request.step_key
    )

@router.get("/generations", response_model=List[SuggestionResponse])
async def gen_get(db: Session = Depends(get_db)):
    generations = crud_generations.get_all_generations(db)
    return generations
