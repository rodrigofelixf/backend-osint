import os

from redis.asyncio import Redis
import json
from typing import Optional

REDIS_DB = os.getenv("REDIS_DB")
redis = Redis.from_url(REDIS_DB)




async def get_cache(key: str) -> Optional[dict]:
    cached_data = await redis.get(key)
    if cached_data:
        return json.loads(cached_data)
    return None


async def set_cache(key: str, value: dict, expire: int = 300):
    await redis.set(key, json.dumps(value), ex=expire)
