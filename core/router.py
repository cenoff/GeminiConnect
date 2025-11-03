import asyncio
from typing import Any
from core.analyzer import Analyzer
from core.classifier import rate_response
from fastapi.responses import StreamingResponse, JSONResponse
from generator import generate, generate_non_stream
from config import SIMPLE_MODEL, COMPLEX_MODEL, LITE_MODEL
from core.data_handler import convert_content

RATE_LIMIT_KEYWORDS = [
    "rate limit",
    "quota",
    "429",
    "limit exceeded",
    "rate_limit_error",
]


async def choose_model(
    is_meta_request: bool,
    user_msg: str,
    has_images: bool,
    has_pdf: bool,
    is_search_request: bool,
):
    if is_meta_request:
        model = LITE_MODEL
    else:
        if user_msg and not has_images and not has_pdf:
            result = await rate_response(user_msg)
            if result is None:
                result = 0.5
            model = COMPLEX_MODEL if result >= 0.6 else SIMPLE_MODEL
        elif is_search_request:
            model = SIMPLE_MODEL
        else:
            model = COMPLEX_MODEL
    return model


async def retry_logic(model, messages, gemini_contents):
    has_error = False
    async for chunk in generate(model, messages, gemini_contents):
        if "[Error:" in chunk:
            has_error = True
            break
        yield chunk

    if has_error:
        async for chunk in generate(SIMPLE_MODEL, messages, gemini_contents):
            yield chunk


async def retry_logic_non_stream(model, user_msg):
    content = await generate_non_stream(model, user_msg)

    if "[Error:" in content:
        content = await generate_non_stream(SIMPLE_MODEL, user_msg)

    return content


async def call_generator(
    stream: bool, is_meta_request: bool, model: str, messages: Any, user_msg: str
):
    gemini_contents = await convert_content(messages)
    if stream and not is_meta_request:
        return StreamingResponse(
            retry_logic(model, messages, gemini_contents),
            media_type="text/event-stream",
        )
    else:
        content = await retry_logic_non_stream(model, user_msg)
        return JSONResponse(
            {
                "id": "chatcmpl-1",
                "object": "chat.completion",
                "created": int(asyncio.get_event_loop().time()),
                "model": model,
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": content},
                        "finish_reason": "stop",
                    }
                ],
            }
        )


async def handle_request(body: Any):
    analyzer = Analyzer()
    messages = body.messages

    stream = body.stream
    (
        user_msg,
        has_images,
        has_pdf,
        is_meta_request,
        is_search_request,
    ) = await analyzer.analyze(messages)

    model = await choose_model(
        is_meta_request, user_msg, has_images, has_pdf, is_search_request
    )

    try:
        return await call_generator(stream, is_meta_request, model, messages, user_msg)
    except Exception as e:
        print(f"Error: {e}")
