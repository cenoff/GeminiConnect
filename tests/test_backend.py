import pytest
from fastapi.testclient import TestClient
from backend import app
from config import MAIN_MODELS

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"message": "OK"}

def test_models():
    response = client.get("/v1/models")
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == len(MAIN_MODELS) + 1
    assert data[0]["id"] == "Auto"
    for item in data:
        assert "id" in item
        assert "object" in item
        assert "created" in item
        assert "owned_by" in item

@pytest.mark.asyncio
async def test_chat_completions(mocker):
    mock_handle_request = mocker.patch("backend.handle_request", return_value={"response": "mocked"})
    
    payload = {
        "model": "gemini-2.5-flash",
        "messages": [{"role": "user", "content": "Hello"}],
        "stream": False
    }
    
    response = client.post("/v1/chat/completions", json=payload)
    assert response.status_code == 200
    assert response.json() == {"response": "mocked"}
    mock_handle_request.assert_called_once()

@pytest.mark.asyncio
async def test_chat_completions_error(mocker):
    mocker.patch("backend.handle_request", side_effect=Exception("Test error"))
    
    payload = {
        "model": "gemini-2.5-flash",
        "messages": [{"role": "user", "content": "Hello"}],
        "stream": False
    }
    

    with pytest.raises(Exception, match="Test error"):
        client.post("/v1/chat/completions", json=payload)
