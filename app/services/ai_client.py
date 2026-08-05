import os
import httpx
import anthropic
from typing import Optional
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.prompt import PromptTemplate
from app.schemas.generation import SuggestionBase

from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        load_dotenv()
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.aimodel = os.getenv("AI_MODEL")

    async def test_generation(
        self, 
        prompt: str) -> str:
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
                    {"role": "user", "content": prompt}
                ]
            )

            output_text = ""
            for block in message.content:
                if block.type == "text":
                    output_text += block.text
                    print(block.text)
            return output_text
        
        except Exception as e:
            err_msg = f"[AnthropicAPI Error]: {type(e).__name__} - {e}"
            print("Anthropic error")
            return err_msg


    async def generate_suggestion(
        self,
        dossier_id: int,
        acht_d_stap: str,
        dossier_context: str,
        db: Optional[Session] = None
    ) -> SuggestionBase:
        """
        Haalt het prompt template op uit de database voor de gegeven 8D stap en voert de AI generatie uit.
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
            # Haal de prompt op uit de database (via PromptTemplate model met in-memory fallback)
            prompt_item = PromptTemplate.get_by_step(db, acht_d_stap) if db else None
            if not prompt_item:
                from app.models.prompt import DEFAULT_8D_PROMPTS
                prompt_item = DEFAULT_8D_PROMPTS.get(acht_d_stap.upper())

            system_prompt = prompt_item.system_prompt if prompt_item else "Je bent een QMS expert."
            step_title = prompt_item.title if prompt_item else acht_d_stap

            # 1. Probeer Anthropic indien API sleutel aanwezig is
            if self.anthropic_api_key:
                try:
                    return await self._call_anthropic(dossier_id, acht_d_stap, dossier_context, system_prompt)
                except Exception as e:
                    print(f"[AIService] Anthropic error, val terug op overige providers: {e}")

            # 2. Probeer OpenAI indien API sleutel aanwezig is
            if self.openai_api_key:
                try:
                    return await self._call_openai(dossier_id, acht_d_stap, dossier_context, system_prompt)
                except Exception as e:
                    print(f"[AIService] OpenAI error, val terug op overige providers: {e}")

            # 3. Probeer Gemini indien API sleutel aanwezig is
            if self.gemini_api_key:
                try:
                    return await self._call_gemini(dossier_id, acht_d_stap, dossier_context, system_prompt)
                except Exception as e:
                    print(f"[AIService] Gemini error, val terug op mock: {e}")

            # Fallback op mock AI generatie met database prompt titel
            return self._generate_mock_suggestion(dossier_id, acht_d_stap, dossier_context, step_title)
        finally:
            if should_close_db and db is not None:
                db.close()

    async def _call_anthropic(self, dossier_id: int, acht_d_stap: str, context: str, system_prompt: str) -> SuggestionBase:
        client = anthropic.AsyncAnthropic(api_key=self.anthropic_api_key)
        response = await client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system=system_prompt,
            messages=[
                {"role": "user", "content": f"Dossier ID: {dossier_id}\nStap: {acht_d_stap}\nContext: {context}"}
            ]
        )
        content = ""
        for block in response.content:
            if block.type == "text":
                content += block.text

        return SuggestionBase(
            dossier_id=dossier_id,
            acht_d_stap=acht_d_stap,
            content=content,
            bullet_points=[line.strip("- ") for line in content.split("\n") if line.strip().startswith("-")],
            confidence_score=0.96
        )

    async def _call_openai(self, dossier_id: int, acht_d_stap: str, context: str, system_prompt: str) -> SuggestionBase:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Dossier ID: {dossier_id}\nStap: {acht_d_stap}\nContext: {context}"}
            ],
            "temperature": 0.7
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(url, json=payload, headers=headers)
            res.raise_for_status()
            data = res.json()
            content = data["choices"][0]["message"]["content"]
            return SuggestionBase(
                dossier_id=dossier_id,
                acht_d_stap=acht_d_stap,
                content=content,
                bullet_points=[line.strip("- ") for line in content.split("\n") if line.strip().startswith("-")],
                confidence_score=0.95
            )

    async def _call_gemini(self, dossier_id: int, acht_d_stap: str, context: str, system_prompt: str) -> SuggestionBase:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{system_prompt}\n\nDossier ID: {dossier_id}\nStap: {acht_d_stap}\nContext: {context}"}
                    ]
                }
            ]
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(url, json=payload)
            res.raise_for_status()
            data = res.json()
            content = data["candidates"][0]["content"]["parts"][0]["text"]
            return SuggestionBase(
                dossier_id=dossier_id,
                acht_d_stap=acht_d_stap,
                content=content,
                bullet_points=[line.strip("- ") for line in content.split("\n") if line.strip().startswith("-")],
                confidence_score=0.92
            )

    def _generate_mock_suggestion(self, dossier_id: int, acht_d_stap: str, context: str, step_title: str) -> SuggestionBase:
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

        return SuggestionBase(
            dossier_id=dossier_id,
            acht_d_stap=acht_d_stap,
            content=content,
            bullet_points=bullet_points,
            confidence_score=0.88
        )
