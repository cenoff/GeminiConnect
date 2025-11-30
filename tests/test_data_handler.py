import pytest
import base64
from core.data_handler import process_file, process_img, convert_content
from schemas import Message

@pytest.mark.asyncio
async def test_process_file_text():
    content = base64.b64encode(b"hello world").decode("utf-8")
    item = {"data": content, "mime_type": "text/plain"}
    result = await process_file(item)
    assert result == {"text": "[Document: text/plain]\nhello world"}

@pytest.mark.asyncio
async def test_process_file_pdf():
    item = {"data": "fake_pdf_data", "mime_type": "application/pdf"}
    result = await process_file(item)
    assert result == {"inline_data": {"mime_type": "application/pdf", "data": "fake_pdf_data"}}

@pytest.mark.asyncio
async def test_process_file_archive():
    item = {"data": "fake_zip", "mime_type": "application/zip"}
    result = await process_file(item)
    assert result == {"text": "[Archive files not supported]"}

@pytest.mark.asyncio
async def test_process_img_valid():
    url = "data:image/png;base64,fake_image_data"
    item = {"image_url": {"url": url}}
    result = await process_img(item)
    assert result == {"inline_data": {"mime_type": "image/png", "data": "fake_image_data"}}

@pytest.mark.asyncio
async def test_process_img_invalid():
    item = {"image_url": {"url": "http://example.com/image.png"}}
    result = await process_img(item)
    assert result is None

@pytest.mark.asyncio
async def test_convert_content_simple():
    messages = [Message(role="user", content="hello")]
    result = await convert_content(messages)
    assert len(result) == 1
    assert result[0]["role"] == "user"
    assert result[0]["parts"][0]["text"] == "hello"

@pytest.mark.asyncio
async def test_convert_content_system():
    messages = [
        Message(role="system", content="be helpful"),
        Message(role="user", content="hello")
    ]
    result = await convert_content(messages)
    assert len(result) == 2
    assert result[0]["role"] == "user"
    assert result[0]["parts"][0]["text"] == "[System]: be helpful"
    assert result[1]["role"] == "user"
    assert result[1]["parts"][0]["text"] == "hello"

@pytest.mark.asyncio
async def test_convert_content_complex():

    content = [
        {"type": "text", "text": "look at this"},
        {"type": "image_url", "image_url": {"url": "data:image/png;base64,data"}},
        {"type": "file", "mime_type": "application/pdf", "data": "pdfdata"}
    ]
    messages = [Message(role="user", content=content)]
    
    result = await convert_content(messages)
    assert len(result) == 1
    parts = result[0]["parts"]
    assert len(parts) == 3
    assert parts[0]["text"] == "look at this"
    assert "inline_data" in parts[1]
    assert parts[1]["inline_data"]["mime_type"] == "image/png"
    assert "inline_data" in parts[2]
    assert parts[2]["inline_data"]["mime_type"] == "application/pdf"

