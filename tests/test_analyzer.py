import pytest
from core.analyzer import Analyzer
from schemas import Message

@pytest.mark.asyncio
async def test_get_user_msg_text():
    analyzer = Analyzer()
    messages = [Message(role="user", content="hello")]
    has_images, user_msg, has_pdf = await analyzer.get_user_msg(messages)
    assert has_images is False
    assert user_msg == "hello"
    assert has_pdf is False

@pytest.mark.asyncio
async def test_get_user_msg_complex():
    analyzer = Analyzer()
    content = [
        {"type": "text", "text": "describe this"},
        {"type": "image_url", "image_url": {"url": "..."}}
    ]
    messages = [Message(role="user", content=content)]
    has_images, user_msg, has_pdf = await analyzer.get_user_msg(messages)
    assert has_images is True
    assert user_msg == "describe this"
    assert has_pdf is False

@pytest.mark.asyncio
async def test_is_meta_request():
    analyzer = Analyzer()
    assert await analyzer.is_meta_request("Generate a concise summary") is True
    assert await analyzer.is_meta_request("hello world") is False

@pytest.mark.asyncio
async def test_is_search_request():
    analyzer = Analyzer()
    assert await analyzer.is_search_request("generating search queries") is True
    assert await analyzer.is_search_request("hello world") is False
