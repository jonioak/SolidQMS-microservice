from fastapi import APIRouter, BackgroundTasks, status
from app.db.database import SessionLocal
from app.models.suggestion import Suggestion
from app.schemas.generation import GenerationRequest, GenerationResponse, WebhookPayload, GenerationTest
from app.services.ai_client import AIService
from app.services.webhook import WebhookService

router = APIRouter(prefix="/api/v1", tags=["Generations"])
ai_service = AIService()
webhook_service = WebhookService()

async def process_generation_background(request: GenerationRequest):
    """
    Achtergrondtaak voor het genereren van AI-advies uit de database prompts en het versturen van de webhook callback.
    """
    step_key = request.step_key
    print(f"[BackgroundWorker] Gestart met AI generatie voor dossier {request.dossier_id}, stap/type '{step_key}'")
    db = None
    try:
        try:
            db = SessionLocal()
        except Exception as e:
            print(f"[BackgroundWorker] Kon geen DB verbinding maken: {e}")
            db = None

        # 1. Haal prompt op uit database & genereer AI advies met NC velden
        suggestion = await ai_service.generate_suggestion(
            dossier_id=request.dossier_id,
            acht_d_stap=step_key,
            dossier_context=request.dossier_context or "",
            db=db,
            nc_excerpt=request.nc_excerpt,
            nc_description=request.nc_description,
            nc_location=request.nc_location,
            nc_comments=request.nc_comments,
            current_analysis=request.current_analysis,
            previous_steps=request.previous_steps
        )
        
        # 2. Sla de gegenereerde suggestie op in de database via Suggestion model
        if db is not None:
            Suggestion.save_suggestion(db, suggestion)

        # 3. Bouw webhook payload
        payload = WebhookPayload(
            dossier_id=request.dossier_id,
            acht_d_stap=step_key,
            status="completed",
            suggestion=suggestion.content,
            metadata={
                "bullet_points": suggestion.bullet_points,
                "confidence_score": suggestion.confidence_score,
                "created_at": suggestion.created_at.isoformat() if suggestion.created_at else None
            }
        )
    except Exception as e:
        print(f"[BackgroundWorker] Fout opgetreden tijdens generatie: {e}")
        payload = WebhookPayload(
            dossier_id=request.dossier_id,
            acht_d_stap=step_key,
            status="failed",
            error=str(e)
        )
    finally:
        if db is not None:
            db.close()

    # 4. Verstuur callback naar monoliet
    await webhook_service.send_callback(request.callback_url, payload)


@router.post("/generations", status_code=status.HTTP_202_ACCEPTED, response_model=GenerationResponse)
async def create_generation(request: GenerationRequest, background_tasks: BackgroundTasks):
    """
    Ontvangt een generatie verzoek van de monoliet, start de achtergrondtaak en geeft 202 Accepted terug.
    """
    background_tasks.add_task(process_generation_background, request)
    return GenerationResponse(
        status="accepted",
        message="Generatie is gestart op de achtergrond",
        dossier_id=request.dossier_id,
        acht_d_stap=request.step_key
    )

@router.post("/ai")
async def gen_test(request: GenerationTest):
    result = await ai_service.test_generation(request.prompt)
    return {"status": "success", "result": result}


async def process_generation_background_a(request: GenerationRequest):
    """
    Achtergrondtaak voor het genereren van AI-advies uit de database prompts en het versturen van de webhook callback.
    """
    step_key = request.step_key
    print(f"[BackgroundWorker] Gestart met AI generatie voor dossier {request.dossier_id}, stap/type '{step_key}'")
    db = None
    try:
        try:
            db = SessionLocal()
        except Exception as e:
            print(f"[BackgroundWorker] Kon geen DB verbinding maken: {e}")
            db = None

        # 1. Haal prompt op uit database & genereer AI advies met NC velden
        suggestion = await ai_service.generation8d(
            dossier_id=request.dossier_id,
            acht_d_stap=step_key,
            dossier_context=request.dossier_context or "",
            db=db,
            nc_excerpt=request.nc_excerpt,
            nc_description=request.nc_description,
            nc_location=request.nc_location,
            nc_comments=request.nc_comments,
            current_analysis=request.current_analysis,
            previous_steps=request.previous_steps
        )
        
        # 2. Sla de gegenereerde suggestie op in de database via Suggestion model
        if db is not None:
            Suggestion.save_suggestion(db, suggestion)

        # 3. Bouw webhook payload
        payload = WebhookPayload(
            dossier_id=request.dossier_id,
            acht_d_stap=step_key,
            status="completed",
            suggestion=suggestion.content,
            metadata={
                "bullet_points": suggestion.bullet_points,
                "confidence_score": suggestion.confidence_score,
                "created_at": suggestion.created_at.isoformat() if suggestion.created_at else None
            }
        )

    except Exception as e:
        print(f"[BackgroundWorker] Fout opgetreden tijdens generatie: {e}")
        payload = WebhookPayload(
            dossier_id=request.dossier_id,
            acht_d_stap=step_key,
            status="failed",
            error=str(e)
        )
    finally:
        if db is not None:
            db.close()

    # 4. Verstuur callback naar monoliet
    await webhook_service.send_callback(request.callback_url, payload)

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
