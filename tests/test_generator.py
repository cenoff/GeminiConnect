import pytest
from generator import generate_non_stream, generate

@pytest.mark.asyncio
async def test_generate_non_stream_success(mocker):
    mocker.patch("generator.shuffle_keys", return_value=["test_key"])
    
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": "generated text"}]}}]
    }
    
    async def mock_post(*args, **kwargs):
        return mock_response
    
    mock_client = mocker.MagicMock()
    mock_client.post = mock_post
    
    mock_client_ctx = mocker.MagicMock()
    mock_client_ctx.__aenter__.return_value = mock_client
    mock_client_ctx.__aexit__.return_value = None
    
    mocker.patch("httpx.AsyncClient", return_value=mock_client_ctx)
    
    result = await generate_non_stream("model", "msg")
    assert result == "generated text"

@pytest.mark.asyncio
async def test_generate_non_stream_failure(mocker):
    mocker.patch("generator.shuffle_keys", return_value=["test_key"])
    
    mock_response = mocker.Mock()
    mock_response.status_code = 500
    
    async def mock_post(*args, **kwargs):
        return mock_response
    
    mock_client = mocker.MagicMock()
    mock_client.post = mock_post
    
    mock_client_ctx = mocker.MagicMock()
    mock_client_ctx.__aenter__.return_value = mock_client
    mock_client_ctx.__aexit__.return_value = None
    
    mocker.patch("httpx.AsyncClient", return_value=mock_client_ctx)
    
    result = await generate_non_stream("model", "msg")
    assert result == "[Error: All API keys failed]"

@pytest.mark.asyncio
async def test_generate_stream_success(mocker):
    mocker.patch("generator.shuffle_keys", return_value=["test_key"])

    mock_response = mocker.MagicMock()
    mock_response.status_code = 200
    

    async def async_lines():
        lines = [
            b'data: {"candidates": [{"content": {"parts": [{"text": "chunk1"}]}}]}',
            b'data: {"candidates": [{"content": {"parts": [{"text": "chunk2"}]}}]}'
        ]
        for line in lines:
            yield line.decode('utf-8')
            
    mock_response.aiter_lines = async_lines
    

    mock_stream_ctx = mocker.MagicMock()
    mock_stream_ctx.__aenter__.return_value = mock_response
    mock_stream_ctx.__aexit__.return_value = None
    

    mock_client = mocker.MagicMock()
    mock_client.stream.return_value = mock_stream_ctx
    

    mock_client_ctx = mocker.MagicMock()
    mock_client_ctx.__aenter__.return_value = mock_client
    mock_client_ctx.__aexit__.return_value = None
    

    mocker.patch("httpx.AsyncClient", return_value=mock_client_ctx)
    
    chunks = []
    async for chunk in generate("model", "msg"):
        chunks.append(chunk)
    

    assert len(chunks) > 0

    assert "chunk1" in chunks[0]

@pytest.mark.asyncio
async def test_generate_stream_error(mocker):
    mocker.patch("generator.shuffle_keys", return_value=["test_key"])

    mock_response = mocker.MagicMock()
    mock_response.status_code = 500
    mock_response.aread.return_value = b"Error details"
    

    mock_stream_ctx = mocker.MagicMock()
    mock_stream_ctx.__aenter__.return_value = mock_response
    mock_stream_ctx.__aexit__.return_value = None
    

    mock_client = mocker.MagicMock()
    mock_client.stream.return_value = mock_stream_ctx
    

    mock_client_ctx = mocker.MagicMock()
    mock_client_ctx.__aenter__.return_value = mock_client
    mock_client_ctx.__aexit__.return_value = None
    
    mocker.patch("httpx.AsyncClient", return_value=mock_client_ctx)
    
    chunks = []
    async for chunk in generate("model", "msg"):
        chunks.append(chunk)
        
    assert len(chunks) > 0
    assert "[Error: All API keys failed]" in chunks[-2]

