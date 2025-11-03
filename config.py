import os
import json
import random
from typing import List
from dotenv import load_dotenv

load_dotenv()

HOST: str = os.getenv("HOST")
PORT: int = int(os.getenv("PORT"))

API_KEYS: List = json.loads(os.getenv("GEMINI_API_KEYS"))

RATE_MODEL: str = os.getenv("RATE_MODEL")
LITE_MODEL: str = os.getenv("LITE_MODEL")
SIMPLE_MODEL: str = os.getenv("BASIC_MODEL")
COMPLEX_MODEL: str = os.getenv("COMPLEX_MODEL")
API_KEY = os.getenv("TOGETHER_API_KEY")
MODEL = os.getenv("TOGETHER_MODEL")


async def shuffle_keys():
    shuffled_keys = API_KEYS.copy()
    random.shuffle(shuffled_keys)
    return shuffled_keys
