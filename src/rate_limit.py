# limiter.py
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from redis.asyncio import Redis

limiter_enabled = False


async def init_rate_limit(redis_url: str):
    global limiter_enabled
    
    try:
        redis = Redis.from_url(
            redis_url,
            encoding="utf-8",
            decode_responses=True
        )
        
        await FastAPILimiter.init(redis)
        limiter_enabled = True

    except Exception:
        # Redis unavailable → limiter off
        limiter_enabled = False


def SafeRateLimiter(times: int, seconds: int):
    if not limiter_enabled:
        # return dependency dummy
        async def dummy():
            return True
        return dummy

    return RateLimiter(times=times, seconds=seconds)
