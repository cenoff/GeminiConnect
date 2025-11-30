import pytest
from core.router import choose_model, retry_logic_non_stream, handle_request
from config import SIMPLE_MODEL, COMPLEX_MODEL, LITE_MODEL

@pytest.mark.asyncio
async def test_choose_model_meta():
    model = await choose_model(True, "msg", False, False, False, "", False)
    assert model == LITE_MODEL

@pytest.mark.asyncio
async def test_choose_model_search():
    model = await choose_model(False, "msg", False, False, True, "", False)
    assert model == SIMPLE_MODEL

@pytest.mark.asyncio
async def test_choose_model_complex(mocker):
    mocker.patch("core.router.rate_response", return_value=0.8)
    model = await choose_model(False, "msg", False, False, False, "", True)
    assert model == COMPLEX_MODEL

@pytest.mark.asyncio
async def test_retry_logic_non_stream_success(mocker):
    mocker.patch("core.router.generate_non_stream", return_value="success")
    result = await retry_logic_non_stream("model", "msg")
    assert result == "success"

@pytest.mark.asyncio
async def test_retry_logic_non_stream_failure(mocker):

    mocker.patch("core.router.generate_non_stream", side_effect=["[Error: failed]", "fallback success"])
    result = await retry_logic_non_stream("model", "msg")
    assert result == "fallback success"

@pytest.mark.asyncio
async def test_call_generator_stream(mocker):
    mocker.patch("core.router.convert_content", return_value="converted")

    mocker.patch("core.router.StreamingResponse", return_value="streaming_response")
    
    from core.router import call_generator
    

    mocker.patch("core.router.retry_logic", return_value="retry_logic_gen")
    
    response = await call_generator(True, False, "model", "msg", "user_msg")
    assert response == "streaming_response"

@pytest.mark.asyncio
async def test_handle_request_integration(mocker):

    mocker.patch("core.router.Analyzer.analyze", return_value=("msg", False, False, False, False))
    mocker.patch("core.router.choose_model", return_value="model")
    mocker.patch("core.router.call_generator", return_value="response")
    
    from core.router import handle_request
    from schemas import ChatCompletionRequest, Message
    
    body = ChatCompletionRequest(model="model", messages=[Message(role="user", content="hello")])
    response = await handle_request(body)
    assert response == "response"

@pytest.mark.asyncio
async def test_handle_request_error(mocker):
    mocker.patch("core.router.Analyzer.analyze", side_effect=Exception("Analysis failed"))
    
    from core.router import handle_request
    from schemas import ChatCompletionRequest, Message
    
    body = ChatCompletionRequest(model="model", messages=[Message(role="user", content="hello")])
    with pytest.raises(Exception, match="Analysis failed"):
        await handle_request(body)

