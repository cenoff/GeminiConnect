import pytest
from core.classifier import rate_response, choose_model

@pytest.mark.asyncio
async def test_rate_response_long(mocker):
    prompt = "a" * 201
    result = await rate_response(prompt)
    assert result == 1

@pytest.mark.asyncio
async def test_rate_response_short(mocker):
    mocker.patch("core.classifier.choose_model", return_value=0.2)
    result = await rate_response("short prompt")
    assert result == 0.2

@pytest.mark.asyncio
async def test_choose_model_success(mocker):
    # Mock shuffle_keys to ensure the loop runs regardless of env vars
    mocker.patch("core.classifier.shuffle_keys", return_value=["fake_key"])

    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": '{"complexity": 0.8}'}]}}]
    }
    
    mock_client = mocker.AsyncMock()
    mock_client.post.return_value = mock_response
    
    mock_client_ctx = mocker.AsyncMock()
    mock_client_ctx.__aenter__.return_value = mock_client
    mock_client_ctx.__aexit__.return_value = None
    
    mocker.patch("httpx.AsyncClient", return_value=mock_client_ctx)
    
    result = await choose_model("test")
    assert result == 0.8

@pytest.mark.asyncio
async def test_choose_model_failure(mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 500
    
    mocker.patch("httpx.AsyncClient.post", return_value=mock_response)
    
    result = await choose_model("test")
    assert result == 0.5
