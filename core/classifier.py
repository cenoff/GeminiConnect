import re
import json
import httpx
from config import RATE_MODEL, shuffle_keys


async def rate_response(prompt: str):
    last_query = prompt.split("Query:")[-1].strip()
    if len(last_query) > 200:
        return 1
    else:
        try:
            result = await choose_model(prompt)
            if result is None:
                result = await choose_model(prompt)
            return result
        except Exception as e:
            print(f"Error: {e}")


async def choose_model(prompt: str):
    shuffled_keys = await shuffle_keys()
    classification_prompt = f"""
        Analyze the request and return JSON: {{"complexity": a number from 0 to 1}}
        complexity should be high (0.6-1.0) for complex tasks: detailed analysis, comparisons, reasoning, long explanations, fixing errors, adding something, changing or correcting.
        complexity should be low (0-0.5) for simple tasks: short answers, facts, basic questions.
        I remind you that your task is not to help the user, but to return, depending on the complexity of the request, {{"complexity": a number from 0.0 to 1.0}}.
        The request whose complexity needs to be assessed: "{prompt}"
        DO NOT RETURN NONE, YOU MUST RETURN JSON WITH A VALUE, OTHERWISE YOU WILL BE SEVERELY PUNISHED
        JSON:
    """
    contents = [{"role": "user", "parts": [{"text": classification_prompt}]}]
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
        except Exception as e:
            print(f"Error with key {key_index}: {e}")
            continue

    return 0.5
