import asyncio
import logging
from fastapi import FastAPI
from schemas import ChatCompletionRequest
from core.router import handle_request
from config import MAIN_MODELS

app = FastAPI()


@app.get("/health")
async def health():
    logging.info("Health endpoint called")
    return {"message": "OK"}


@app.get("/v1/models")
async def models():
    model_list = [
        {
            "id": "Auto",
            "object": "model",
            "created": int(asyncio.get_event_loop().time()),
            "owned_by": "system",
        }
    ]

    for model_id in MAIN_MODELS:
        model_list.append(
            {
                "id": model_id,
                "object": "model",
                "created": int(asyncio.get_event_loop().time()),
                "owned_by": "system",
            }
        )

    logging.info("Models endpoint called")
    return {"data": model_list}


@app.post("/v1/chat/completions")
async def generate_answer(body: ChatCompletionRequest):
    logging.info(
        f"chat/completions endpoint called - model: {body.model}, "
        f"stream: {body.stream}, messages: {len(body.messages)}"
    )
    try:
        return await handle_request(body)
    except Exception as e:
        logging.error(f"Error in generate_answer: {e}", exc_info=True)
        raise
