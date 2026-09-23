import os
import time
import anthropic

from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        load_dotenv()
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.aimodel = os.getenv("AI_MODEL")


    async def generate_ai_response(self, prompt_text: str) -> dict:
        """
        Genereert een AI response op basis van een prompt template en input context.
        """
        start_time = time.time()
        duration_ms = 0

        if not self.anthropic_api_key:
            print("Geen ANTHROPIC_API_KEY gevonden")
            return {"error": "Geen ANTHROPIC_API_KEY gevonden"}

        try:
            client = anthropic.AsyncAnthropic(api_key=self.anthropic_api_key)

            response = await client.messages.create(
                model=self.aimodel,
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt_text}
                ]
            )

            duration_ms = int((time.time() - start_time) * 1000)
            
            return {
                "status": "completed",
                "output_text": response.content[0].text,
                "input_token_count": response.usage.input_tokens,
                "output_token_count": response.usage.output_tokens,
                "model_version": self.aimodel,
                "generation_duration": duration_ms,
                "error_message": None
            }
            
        except Exception as e:
            # Vang netjes API-errors af (bijv. timeouts of te weinig credits)
            duration_ms = int((time.time() - start_time) * 1000)
            
            return {
                "status": "failed",
                "output_text": None,
                "input_token_count": None,
                "output_token_count": None,
                "model_version": self.aimodel,
                "generation_duration": duration_ms,
                "error_message": f"Anthropic API Error: {str(e)}"
            }

ai_client = AIService()   