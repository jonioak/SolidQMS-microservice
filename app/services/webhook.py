import httpx
from app.schemas.generation import WebhookPayload

class WebhookService:
    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout

    async def send_callback(self, callback_url: str, payload: WebhookPayload) -> bool:
        """
        Verstuur het resultaat van de AI-generatie asynchroon naar de opgeven callback URL van de monoliet.
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(callback_url, json=payload.model_dump())
                response.raise_for_status()
                print(f"[WebhookService] Callback succesvol verzonden naar {callback_url} (Status: {response.status_code})")
                return True
        except Exception as e:
            print(f"[WebhookService] Fout bij verzenden callback naar {callback_url}: {e}")
            return False
