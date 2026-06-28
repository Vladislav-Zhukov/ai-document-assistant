from fastapi import HTTPException, status
from redis.asyncio import Redis

from app.core.config import settings


redis_client = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True,
)


async def check_rate_limit(user_id: int, action: str) -> None:
    key = f"rate_limit:{action}:{user_id}"

    current = await redis_client.incr(key)

    if current == 1:
        await redis_client.expire(key, settings.RATE_LIMIT_WINDOW_SECONDS)

    if current > settings.RATE_LIMIT_REQUESTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later.",
        )