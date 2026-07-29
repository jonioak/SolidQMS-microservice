from fastapi import APIRouter, BackgroundTasks, status
from app.schemas.generation import GenerationRequest, GenerationResponse, WebhookPayload
from app.services.ai_client import AIService
from app.services.webhook import WebhookService

router = APIRouter(prefix="/api/v1", tags=["Generations"])
ai_service = AIService()
webhook_service = WebhookService()

async def process_generation_background(request: GenerationRequest):
    """
    Achtergrondtaak voor het genereren van AI-advies en het versturen van de webhook callback.
    """
    print(f"[BackgroundWorker] Gestart met AI generatie voor dossier {request.dossier_id}, stap {request.acht_d_stap}")
    try:
        suggestion = await ai_service.generate_suggestion(
            dossier_id=request.dossier_id,
            acht_d_stap=request.acht_d_stap,
            dossier_context=request.dossier_context
        )
        
        payload = WebhookPayload(
            dossier_id=request.dossier_id,
            acht_d_stap=request.acht_d_stap,
            status="completed",
            suggestion=suggestion.content,
            metadata={
                "bullet_points": suggestion.bullet_points,
                "confidence_score": suggestion.confidence_score
            }
        )
    except Exception as e:
        print(f"[BackgroundWorker] Fout opgetreden tijdens generatie: {e}")
        payload = WebhookPayload(
            dossier_id=request.dossier_id,
            acht_d_stap=request.acht_d_stap,
            status="failed",
            error=str(e)
        )

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
        acht_d_stap=request.acht_d_stap
    )
