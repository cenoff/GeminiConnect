import pytest
from core.analyzer import Analyzer
from schemas import Message

@pytest.mark.asyncio
async def test_get_user_msg_no_type_and_join():
    analyzer = Analyzer()
    content = [
        {"text": "hello"},
        {"text": " world"},
        {"type": "image_url", "image_url": {"url": "..."}}
    ]
    messages = [Message(role="user", content=content)]
    has_images, user_msg, has_pdf = await analyzer.get_user_msg(messages)
    assert has_images is True
    assert user_msg == "hello  world"
    assert has_pdf is False
