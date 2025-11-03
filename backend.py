import asyncio
from fastapi import FastAPI
from schemas import ChatCompletionRequest
from core.router import handle_request

app = FastAPI()


@app.get("/health")
async def health():
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
    return {"data": model_list}


@app.post("/v1/chat/completions")
async def generate_answer(body: ChatCompletionRequest):
    return await handle_request(body)
