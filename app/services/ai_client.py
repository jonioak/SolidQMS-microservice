import os
import httpx
from typing import Optional
from app.models.prompt import DEFAULT_8D_PROMPTS
from app.models.suggestion import Suggestion

class AIService:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")

    async def generate_suggestion(self, dossier_id: int, acht_d_stap: str, dossier_context: str) -> Suggestion:
        prompt_template = DEFAULT_8D_PROMPTS.get(acht_d_stap.upper())
        system_prompt = prompt_template.system_prompt if prompt_template else "Je bent een QMS expert."

        # Probeer OpenAI indien API sleutel aanwezig is
        if self.openai_api_key:
            try:
                return await self._call_openai(dossier_id, acht_d_stap, dossier_context, system_prompt)
            except Exception as e:
                print(f"[AIService] OpenAI error, val terug op mock: {e}")

        # Probeer Gemini indien API sleutel aanwezig is
        if self.gemini_api_key:
            try:
                return await self._call_gemini(dossier_id, acht_d_stap, dossier_context, system_prompt)
            except Exception as e:
                print(f"[AIService] Gemini error, val terug op mock: {e}")

        # Fallback op mock AI generatie
        return self._generate_mock_suggestion(dossier_id, acht_d_stap, dossier_context)

    async def _call_openai(self, dossier_id: int, acht_d_stap: str, context: str, system_prompt: str) -> Suggestion:
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
            return Suggestion(
                dossier_id=dossier_id,
                acht_d_stap=acht_d_stap,
                content=content,
                bullet_points=[line.strip("- ") for line in content.split("\n") if line.strip().startswith("-")],
                confidence_score=0.95
            )

    async def _call_gemini(self, dossier_id: int, acht_d_stap: str, context: str, system_prompt: str) -> Suggestion:
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
            return Suggestion(
                dossier_id=dossier_id,
                acht_d_stap=acht_d_stap,
                content=content,
                bullet_points=[line.strip("- ") for line in content.split("\n") if line.strip().startswith("-")],
                confidence_score=0.92
            )

    def _generate_mock_suggestion(self, dossier_id: int, acht_d_stap: str, context: str) -> Suggestion:
        step = acht_d_stap.upper()
        title = DEFAULT_8D_PROMPTS.get(step, None)
        step_title = title.title if title else step

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

        return Suggestion(
            dossier_id=dossier_id,
            acht_d_stap=acht_d_stap,
            content=content,
            bullet_points=bullet_points,
            confidence_score=0.88
        )
