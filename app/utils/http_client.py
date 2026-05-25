from collections.abc import AsyncGenerator

import httpx

from app.core.config import Settings, get_settings


async def get_http_client(
    settings: Settings = get_settings(),
) -> AsyncGenerator[httpx.AsyncClient, None]:
    timeout = httpx.Timeout(settings.request_timeout_seconds)
    limits = httpx.Limits(max_connections=50, max_keepalive_connections=20)

    async with httpx.AsyncClient(timeout=timeout, limits=limits) as client:
        yield client
