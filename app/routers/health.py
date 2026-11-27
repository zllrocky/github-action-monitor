import asyncio
import asyncpg
import aio_pika
import redis.asyncio
from fastapi import APIRouter, Response, status
from app.core.config import get_settings

health_router = APIRouter()


async def _check_postgres(dsn: str) -> bool:
    normalized_dsn = dsn.replace("postgresql+asyncpg://", "postgresql://", 1)
    conn = await asyncpg.connect(dsn=normalized_dsn)
    try:
        await conn.execute('SELECT 1')
        return True
    finally:
        await conn.close()


async def check_postgres(dsn: str) -> bool:
    try:
        return await asyncio.wait_for(_check_postgres(dsn), timeout=1.0)
    except Exception:
        return False


async def _check_redis(url: str) -> bool:
    client = redis.asyncio.from_url(url)
    try:
        pong = await client.ping()
        return bool(pong)
    finally:
        await client.close()


async def check_redis(url: str) -> bool:
    try:
        return await asyncio.wait_for(_check_redis(url), timeout=1.0)
    except Exception:
        return False


async def _check_rabbitmq(url: str) -> bool:
    conn = await aio_pika.connect(url)
    try:
        return not conn.is_closed
    finally:
        await conn.close()


async def check_rabbitmq(url: str) -> bool:
    try:
        return await asyncio.wait_for(_check_rabbitmq(url), timeout=1.0)
    except Exception:
        return False


@health_router.get("/health")
async def get_health(response: Response):
    settings = get_settings()

    checks = [
        ('postgres', lambda: check_postgres(settings.POSTGRES_DSN)),
        ('redis', lambda: check_redis(settings.REDIS_URL)),
        ('rabbitmq', lambda: check_rabbitmq(settings.RABBITMQ_URL)),
    ]

    for name, make_cor in checks:
        ok = await make_cor()
        if not ok:
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            return {'status': 'error', 'dependency': name}
    response.status_code = status.HTTP_200_OK
    return {'status': 'ok'}
