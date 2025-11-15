import asyncio
import logging
from typing import Any
from core.analyzer import Analyzer
from core.classifier import rate_response
from fastapi.responses import StreamingResponse, JSONResponse
from generator import generate, generate_non_stream
from config import SIMPLE_MODEL, COMPLEX_MODEL, LITE_MODEL, MAIN_MODELS
from core.data_handler import convert_content


async def choose_model(
    is_meta_request: bool,
    user_msg: str,
    has_images: bool,
    has_pdf: bool,
    is_search_request: bool,
    model: str,
):
    if is_meta_request:
        model = LITE_MODEL

    if is_search_request:
        model = SIMPLE_MODEL

    if model and model in MAIN_MODELS:
        return model

    if user_msg and not has_images and not has_pdf:
        logging.info("Rating response.")
        result = await rate_response(user_msg)
        if result is None:
            result = 0.5
        model = COMPLEX_MODEL if result >= 0.6 else SIMPLE_MODEL
        logging.info(
            f"Response was rated as {'simple' if result <= 0.5 else 'complex'}"
        )
    # elif is_search_request:
    #     model = SIMPLE_MODEL
    else:
        model = COMPLEX_MODEL

    logging.info(f"returned: {model}")
    return model


async def retry_logic(model, messages, gemini_contents):
    has_error = False

    async for chunk in generate(model, messages, gemini_contents):
        if "[Error:" in chunk:
            logging.error(f"Caught error in chunk: {chunk}")
            has_error = True
            break
        yield chunk

    if has_error:
        logging.info(f"Falling back to {SIMPLE_MODEL}.")
        async for chunk in generate(SIMPLE_MODEL, messages, gemini_contents):
            yield chunk


async def retry_logic_non_stream(model, user_msg):
    content = await generate_non_stream(model, user_msg)

    if "[Error:" in content:
        logging.error(
            f"Caught error in chunk: {content}\nFalling back to {SIMPLE_MODEL}."
        )
        content = await generate_non_stream(SIMPLE_MODEL, user_msg)

    return content


async def call_generator(
    stream: bool, is_meta_request: bool, model: str, messages: Any, user_msg: str
):
    gemini_contents = await convert_content(messages)
    if stream and not is_meta_request:
        logging.info(f"Generating streaming response with model: {model}")
        return StreamingResponse(
            retry_logic(model, messages, gemini_contents),
            media_type="text/event-stream",
        )
    else:
        logging.info(f"Generating non-streaming response with model: {model}")
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
    model = body.model
    messages = body.messages

    logging.info(
        f"Handling request - requested model: {model}, stream: {body.stream}, messages: {len(messages)}"
    )

    stream = body.stream
    (
        user_msg,
        has_images,
        has_pdf,
        is_meta_request,
        is_search_request,
    ) = await analyzer.analyze(messages)

    logging.debug(
        f"Analysis results - has_images: {has_images}, has_pdf: {has_pdf}, "
        f"is_meta_request: {is_meta_request}, is_search_request: {is_search_request}"
    )

    model = await choose_model(
        is_meta_request, user_msg, has_images, has_pdf, is_search_request, model
    )

    try:
        return await call_generator(stream, is_meta_request, model, messages, user_msg)

    except Exception as e:
        logging.error(f"Error in handle_request: {e}", exc_info=True)
        raise
