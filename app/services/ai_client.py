import os
import time
from typing import Optional
import anthropic
from dotenv import load_dotenv

from app.interfaces.ai_provider import BaseAIProvider, AIResponse

load_dotenv()

class AnthropicAIProvider(BaseAIProvider):

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.anthropic_api_key = api_key if api_key is not None else os.getenv("ANTHROPIC_API_KEY")
        self.aimodel = model or os.getenv("AI_MODEL", "claude-3-5-sonnet-20241022")

    async def generate_response(self, prompt_text: str) -> AIResponse:
        start_time = time.time()

        if not self.anthropic_api_key:
            return AIResponse(
                status="failed",
                model_version=self.aimodel,
                generation_duration=0,
                error_message="Geen ANTHROPIC_API_KEY gevonden"
            )

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
            return AIResponse(
                status="completed",
                output_text=response.content[0].text,
                input_token_count=response.usage.input_tokens,
                output_token_count=response.usage.output_tokens,
                model_version=self.aimodel,
                generation_duration=duration_ms,
                error_message=None
            )
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            return AIResponse(
                status="failed",
                output_text=None,
                input_token_count=None,
                output_token_count=None,
                model_version=self.aimodel,
                generation_duration=duration_ms,
                error_message=f"Anthropic API Error: {str(e)}"
            )

    async def generate_ai_response(self, prompt_text: str) -> dict:
        response = await self.generate_response(prompt_text)
        return response.model_dump()


# Mock AI Provider voor lokale unit tests.
class MockAIProvider(BaseAIProvider):

    def __init__(self, mock_output: str):
        self.mock_output = mock_output

    async def generate_response(self, prompt_text: str) -> AIResponse:
        return AIResponse(
            status="completed",
            output_text=self.mock_output,
            input_token_count=42,
            output_token_count=128,
            model_version="mock-ai",
            generation_duration=10,
            error_message=None
        )

    async def generate_ai_response(self, prompt_text: str) -> dict:
        response = await self.generate_response(prompt_text)
        return response.model_dump()


# Singleton
ai_client = AnthropicAIProvider()