import re
import json
import httpx
import logging
from config import RATE_MODEL, shuffle_keys, classification_prompt


async def rate_response(prompt: str):
    if len(prompt) > 200:
        logging.info(
            f"Query length ({len(prompt)} chars) > 200, rated as complex (1.0)"
        )
        return 1
    else:
        try:
            result = await choose_model(prompt)
            if result is None:
                logging.warning("First classification attempt returned None, retrying")
                result = await choose_model(prompt)
            return result
        except Exception as e:
            logging.error(f"Error in rate_response: {e}")
            raise


async def choose_model(prompt: str):
    shuffled_keys = await shuffle_keys()

    contents = [
        {
            "role": "user",
            "parts": [{"text": classification_prompt.format(prompt=prompt)}],
        }
    ]
    payload = {
        "contents": contents,
        "generationConfig": {"maxOutputTokens": 150, "temperature": 0.0},
    }

    for key_index, api_key in enumerate(shuffled_keys):
        url = f"https://generativelanguage.googleapis.com/v1/models/{RATE_MODEL}:generateContent?key={api_key}"
        try:
            async with httpx.AsyncClient(timeout=None, http2=True) as client:
                response = await client.post(
                    url, json=payload, headers={"Content-Type": "application/json"}
                )
                if response.status_code == 200:
                    answer = response.json()["candidates"][0]["content"]["parts"][0][
                        "text"
                    ]
                    json_match = re.search(r"\{[^}]+\}", answer)
                    if json_match:
                        parsed = json.loads(json_match.group())
                        return float(parsed.get("complexity", 0.5))
                    else:
                        logging.info("Answer is empty - retrying.")
                else:
                    logging.info(
                        f"Error - response status code: {response.status_code}"
                    )
        except Exception as e:
            logging.info(
                f"Error with classifying model with key {key_index}: {e}, retrying"
            )
            continue

    return 0.5
