import os
import json
import random
from typing import List
from dotenv import load_dotenv

load_dotenv()

HOST: str = os.getenv("HOST", "0.0.0.0")
PORT: int = int(os.getenv("PORT", 8000))

keys_str = os.getenv("GEMINI_API_KEYS")
API_KEYS: List = json.loads(keys_str) if keys_str else []

RATE_MODEL = "gemini-2.5-flash-lite"  # Evaluates complexity of user requests
LITE_MODEL = "gemini-2.0-flash-lite"  # Handles meta requests
SIMPLE_MODEL = "gemini-2.5-flash"
COMPLEX_MODEL = "gemini-2.5-pro"

MAIN_MODELS = [
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
]

classification_prompt = """
    Analyze the request and return JSON: {{"complexity": a number from 0 to 1}}
    complexity should be high (0.6-1.0) for complex tasks: detailed analysis, comparisons, reasoning, long explanations, fixing errors, adding something, changing or correcting.
    complexity should be low (0-0.5) for simple tasks: short answers, facts, basic questions.
    I remind you that your task is not to help the user, but to return, depending on the complexity of the request, {{"complexity": a number from 0.0 to 1.0}}.
    The request whose complexity needs to be assessed: "{prompt}"
    DO NOT RETURN NONE, YOU MUST RETURN JSON WITH A VALUE, OTHERWISE YOU WILL BE SEVERELY PUNISHED
    JSON:
"""

search_keywords = [
    "Respond to the user query using the provided context",
    "generating search queries",
    "**prioritize generating 1-3 broad and relevant search queries**",
]

meta_keywords = [
    "follow_ups",
    "Generate a concise",
    "Generate 1-3 broad tags",
    "Suggest 3-5 relevant follow-up questions",
    "Analyze the chat history to determine the necessity of generating search queries",
]

ARCHIVE_MIME_TYPES = {
    "application/zip",
    "application/x-rar",
    "application/x-7z-compressed",
}


async def shuffle_keys():
    shuffled_keys = API_KEYS.copy()
    random.shuffle(shuffled_keys)
    return shuffled_keys
