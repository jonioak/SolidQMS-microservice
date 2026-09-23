import os
import time
import httpx
import anthropic
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.prompt import PromptTemplate
from app.schemas.task_schema import TaskUpdate
from dotenv import load_dotenv
from fastapi import HTTPException

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

        

    async def test_task(self, prompt_template: str, input_context: dict) -> str:
        """
        Test functie om de Anthropic API direct aan te roepen.
        """
        if not self.anthropic_api_key:
            print("Geen ANTHROPIC_API_KEY gevonden")
            return "Geen ANTHROPIC_API_KEY gevonden"

        try:
            client = anthropic.AsyncAnthropic(api_key=self.anthropic_api_key)

             # Vul de variabelen (zoals {nc_excerpt}) in de tekst in
            formatted_prompt = prompt_template
            for key, value in input_context.items():
                formatted_prompt = formatted_prompt.replace(f"{{{key}}}", str(value))

            response = await client.messages.create(
                model=self.aimodel,
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": formatted_prompt}
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            print(f"AI Error: {e}")
            raise HTTPException(status_code=500, detail="Kon geen verbinding maken met de AI-provider.")
    

    async def task8d(
            self,
            dossier_id: int,
            acht_d_stap: str,
            dossier_context: str = "",
            db: Optional[Session] = None,
            nc_excerpt: Optional[str] = None,
            nc_description: Optional[str] = None,
            nc_location: Optional[str] = None,
            nc_comments: Optional[str] = None,
            current_analysis: Optional[str] = None,
            previous_steps: Optional[str] = None
            ) -> str:
            """
            Test functie om de Anthropic API direct aan te roepen.
            """
            if not self.anthropic_api_key:
                print("Geen ANTHROPIC_API_KEY gevonden")
                return "Geen ANTHROPIC_API_KEY gevonden"
    
            try:
                client = anthropic.AsyncAnthropic(api_key=self.anthropic_api_key)
                    
                message = await client.messages.create(
                    model=self.aimodel,
                    max_tokens=1024,
                    messages=[
                        {"role": "user", "content": acht_d_stap}
                    ] )
    
                output_text = ""
                for block in message.content:
                    if block.type == "text":
                        output_text += block.text
                        print(block.text)
                return output_text
            
            except Exception as e:
                err_msg = f"[AnthropicAPI Error]: {type(e).__name__} - {e}"
                print(f"Anthropic error: {err_msg}")
                return err_msg
    

    def _interpolate_prompt(self, template: str, context_vars: Dict[str, Any]) -> str:
        """Symptoom & NC variabele vervanging voor Ruby monoliet %{var} en {var} placeholders"""
        rendered = template
        for k, v in context_vars.items():
            val = str(v) if v is not None else ""
            rendered = rendered.replace(f"%{{{k}}}", val)
            rendered = rendered.replace(f"{{{k}}}", val)
        return rendered


ai_client = AIService()   