import pytest
from config import shuffle_keys, API_KEYS

@pytest.mark.asyncio
async def test_shuffle_keys():
    keys = await shuffle_keys()
    assert len(keys) == len(API_KEYS)
    assert set(keys) == set(API_KEYS)
