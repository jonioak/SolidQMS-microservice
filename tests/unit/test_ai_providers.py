import asyncio
from app.interfaces.ai_provider import BaseAIProvider, AIResponse
from app.services.ai_client import MockAIProvider, AnthropicAIProvider


def test_u10_mock_ai_provider_response():

    # Arrange
    provider: BaseAIProvider = MockAIProvider(mock_output="Dit is een testanalyse.")

    # Act
    response: AIResponse = asyncio.run(provider.generate_response("Test prompt"))

    # Assert
    assert response.status == "completed"
    assert response.output_text == "Dit is een testanalyse."
    assert response.model_version == "mock-ai"


def test_u11_anthropic_provider_zonder_api_key_faalt_netjes():

    # Arrange
    provider: BaseAIProvider = AnthropicAIProvider(api_key="")

    # Act
    response: AIResponse = asyncio.run(provider.generate_response("Test prompt"))

    # Assert
    assert response.status == "failed"
    assert "Geen ANTHROPIC_API_KEY" in response.error_message
