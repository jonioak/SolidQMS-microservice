from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel, ConfigDict


class AIResponse(BaseModel):

    status: str
    output_text: Optional[str] = None
    input_token_count: Optional[int] = None
    output_token_count: Optional[int] = None
    model_version: Optional[str] = None
    generation_duration: Optional[int] = None
    error_message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# Abstracte basisklasse voor AI providers (Open/Closed Principle).
class BaseAIProvider(ABC):

    @abstractmethod
    async def generate_response(self, prompt_text: str) -> AIResponse:
        pass
