import asyncio
from app.interfaces.ai_provider import BaseAIProvider, AIResponse
from app.services.ai_client import MockAIProvider, AnthropicAIProvider


def test_u10_mock_ai_provider_response():

    # Arrange
    provider: BaseAIProvider = MockAIProvider(mock_output="Dit is een testanalyse.")

    # Act
    response: AIResponse = asyncio.run(provider.generate_response("Test prompt"))

    # Assert
    assert isinstance(response, AIResponse)
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


def test_u12_lsp_providers_zijn_volledig_uitwisselbaar():

    # Arrange
    def voer_ai_taak_uit(provider: BaseAIProvider, prompt: str) -> AIResponse:
        return asyncio.run(provider.generate_response(prompt))

    # Act
    # Test 1: Roep aan met MockAIProvider
    mock_provider = MockAIProvider(mock_output="8D Analyse voltooid.")
    mock_response = voer_ai_taak_uit(mock_provider, "Prompt A")

    # Test 2: Roep aan met AnthropicAIProvider
    anthropic_provider = AnthropicAIProvider(api_key="")
    anthropic_response = voer_ai_taak_uit(anthropic_provider, "Prompt B")

    # Beide implementaties leveren hetzelfde AIResponse contract op (LSP)
    assert isinstance(mock_response, AIResponse)
    assert isinstance(anthropic_response, AIResponse)
    assert mock_response.status == "completed"
    assert anthropic_response.status == "failed"
