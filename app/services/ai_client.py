import os
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
            
            # 3. Geef alleen de tekst terug
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

    async def generate_suggestion(
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
    ) -> TaskUpdate:
        """
        Haalt het prompt template op uit de database voor de gegeven 8D stap/sleutel,
        vervangt de QMS/NC variabelen en voert de AI generatie uit.
        """
        should_close_db = False
        if db is None:
            try:
                db = SessionLocal()
                should_close_db = True
            except Exception as e:
                print(f"[AIService] Kon geen DB sessie openen: {e}")
                db = None

        try:
            # Haal de prompt op uit de database
            prompt_item = PromptTemplate.get_by_step(db, acht_d_stap) if db else None
            if not prompt_item:
                from app.models.prompt import DEFAULT_8D_PROMPTS
                prompt_item = DEFAULT_8D_PROMPTS.get(acht_d_stap.upper())

            raw_prompt_text = prompt_item.prompt_text if prompt_item else "Je bent een QMS expert."
            step_title = prompt_item.title if prompt_item else acht_d_stap

            # Bouw context variabelen voor %{nc_excerpt}, %{nc_description}, etc.
            context_vars = {
                "nc_excerpt": nc_excerpt or dossier_context,
                "nc_description": nc_description or dossier_context,
                "nc_location": nc_location or "N/B",
                "nc_comments": nc_comments or "",
                "current_analysis": current_analysis or dossier_context,
                "previous_steps": previous_steps or "",
                "dossier_context": dossier_context
            }

            prompt_text = self._interpolate_prompt(raw_prompt_text, context_vars)

            if self.anthropic_api_key:
                try:
                    return await self._call_anthropic(dossier_id, acht_d_stap, dossier_context, prompt_text)
                except Exception as e:
                    print(f"[AIService] Anthropic error, val terug op overige providers: {e}")

            return self._generate_mock_suggestion(dossier_id, acht_d_stap, dossier_context, step_title)
        finally:
            if should_close_db and db is not None:
                db.close()

    async def _call_anthropic(self, dossier_id: int, acht_d_stap: str, context: str, prompt_text: str) -> TaskUpdate:
        client = anthropic.AsyncAnthropic(api_key=self.anthropic_api_key)
        response = await client.messages.create(
            model=self.aimodel,
            max_tokens=1024,
            system=prompt_text,
            messages=[
                {"role": "user", "content": f"Dossier ID: {dossier_id}\nStap: {acht_d_stap}\nContext: {context}"}
            ]
        )
        content = ""
        for block in response.content:
            if block.type == "text":
                content += block.text

        return TaskUpdate(
            dossier_id=dossier_id,
            acht_d_stap=acht_d_stap,
            content=content,
            bullet_points=[line.strip("- ") for line in content.split("\n") if line.strip().startswith("-")],
            confidence_score=0.96
        )

    def _generate_mock_suggestion(self, dossier_id: int, acht_d_stap: str, context: str, step_title: str) -> TaskUpdate:
        step = acht_d_stap.upper()

        content = (
            f"AI Advies voor {step} ({step_title}) - Dossier #{dossier_id}:\n"
            f"Gebaseerd op de opgegeven context: '{context}'\n\n"
            f"Aanbevolen acties:\n"
            f"- Analyseer de gerelateerde procesparameters en historische data.\n"
            f"- Documenteer de bevindingen in het SolidQMS kwaliteitsdossier.\n"
            f"- Verifieer de effectiviteit van de voorgestelde acties met de kwaliteitsmanager."
        )

        bullet_points = [
            "Analyseer de gerelateerde procesparameters en historische data.",
            "Documenteer de bevindingen in het SolidQMS kwaliteitsdossier.",
            "Verifieer de effectiviteit van de voorgestelde acties met de kwaliteitsmanager."
        ]

        return TaskUpdate(
            dossier_id=dossier_id,
            acht_d_stap=acht_d_stap,
            content=content,
            bullet_points=bullet_points,
            confidence_score=0.88
        )

    