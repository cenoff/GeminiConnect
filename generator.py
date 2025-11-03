import json
import httpx
import asyncio
from typing import Any
from config import shuffle_keys


async def generate(
    MODEL: str, messages: list, gemini_contents: Any, max_retries: int = 0
):
    shuffled_keys = await shuffle_keys()

    url = f"https://generativelanguage.googleapis.com/v1/models/{MODEL}:streamGenerateContent"

    headers = {
        "Content-Type": "application/json",
    }

    payload = {
        "contents": gemini_contents,
        "generationConfig": {
            "maxOutputTokens": 65000,
            "temperature": 0.7,
        },
    }

    for key_index, key in enumerate(shuffled_keys):
        params = {"key": key, "alt": "sse"}

        for attempt in range(max_retries + 1):
            print(
                f"[KEY {key_index + 1}/{len(shuffled_keys)}] Attempt {attempt + 1}/{max_retries + 1} with key {key[:6]}... on model {MODEL}"
            )

            try:
                async with httpx.AsyncClient(timeout=None, http2=True) as client:
                    async with client.stream(
                        "POST", url, json=payload, headers=headers, params=params
                    ) as response:
                        print(f"Response status: {response.status_code}")

                        if response.status_code != 200:
                            error_text = await response.aread()
                            error_str = error_text.decode("utf-8", errors="ignore")
                            print(f"API Error {response.status_code} - trying next key")
                            print(error_str)
                            break

                        chunk_count = 0
                        async for line in response.aiter_lines():
                            line = line.strip()
                            if not line or not line.startswith("data:"):
                                continue

                            try:
                                data = json.loads(line[6:])
                                text = data["candidates"][0]["content"]["parts"][0][
                                    "text"
                                ]
                                if text:
                                    chunk_count += 1
                                    openai_chunk = {
                                        "id": f"chatcmpl-{chunk_count}",
                                        "object": "chat.completion.chunk",
                                        "created": int(asyncio.get_event_loop().time()),
                                        "model": MODEL,
                                        "choices": [
                                            {
                                                "index": 0,
                                                "delta": {"content": text},
                                                "finish_reason": None,
                                            }
                                        ],
                                    }
                                    yield f"data: {json.dumps(openai_chunk)}\n\n"
                            except Exception as e:
                                print(e)
                                pass

                        if chunk_count > 0:
                            final_chunk = {
                                "id": f"chatcmpl-{chunk_count + 1}",
                                "object": "chat.completion.chunk",
                                "created": int(asyncio.get_event_loop().time()),
                                "model": MODEL,
                                "choices": [
                                    {
                                        "index": 0,
                                        "delta": {},
                                        "finish_reason": "stop",
                                    }
                                ],
                            }
                            yield f"data: {json.dumps(final_chunk)}\n\n"
                            yield "data: [DONE]\n\n"
                            return
                        else:
                            break

            except Exception as e:
                print(f"Exception: {e}")
                if attempt < max_retries:
                    await asyncio.sleep(2**attempt)
                    continue
                else:
                    break

    print("All keys exhausted - returning error")
    error_chunk = {
        "id": "chatcmpl-error",
        "object": "chat.completion.chunk",
        "created": int(asyncio.get_event_loop().time()),
        "model": MODEL,
        "choices": [
            {
                "index": 0,
                "delta": {"content": "[Error: All API keys failed]"},
                "finish_reason": "stop",
            }
        ],
    }
    yield f"data: {json.dumps(error_chunk)}\n\n"
    yield "data: [DONE]\n\n"


async def generate_non_stream(MODEL: str, user_msg: str, max_retries: int = 0):
    shuffled_keys = await shuffle_keys()

    url = f"https://generativelanguage.googleapis.com/v1/models/{MODEL}:generateContent"

    headers = {
        "Content-Type": "application/json",
    }

    payload = {
        "contents": [{"role": "user", "parts": [{"text": user_msg}]}],
    }

    for key_index, key in enumerate(shuffled_keys):
        params = {"key": key}

        for attempt in range(max_retries + 1):
            print(
                f"[NON-STREAM KEY {key_index + 1}/{len(shuffled_keys)}] Attempt {attempt + 1}/{max_retries + 1}"
            )

            try:
                async with httpx.AsyncClient(timeout=None) as client:
                    response = await client.post(
                        url, json=payload, headers=headers, params=params
                    )

                    if response.status_code == 200:
                        data = response.json()
                        text = data["candidates"][0]["content"]["parts"][0]["text"]
                        if text:
                            return text
                    else:
                        print(f"API Error {response.status_code} - trying next key")
                        break

            except Exception as e:
                print(f"Exception: {e}")
                if attempt < max_retries:
                    await asyncio.sleep(2**attempt)
                    continue
                else:
                    break

    return "[Error: All API keys failed]"
