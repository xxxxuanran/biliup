import asyncio

import httpx


DEFAULT_HTTP_TIMEOUT = 15.0

TIMEOUT = httpx.Timeout(
    timeout=120.0,
    connect=DEFAULT_HTTP_TIMEOUT,
    pool=30.0
)
LIMITS = httpx.Limits(
    max_connections=1000,
    max_keepalive_connections=100,
    keepalive_expiry=3.0
)

client = httpx.AsyncClient(
    http2=True,
    follow_redirects=True,
    timeout=TIMEOUT,
    limits=LIMITS
)

loop = asyncio.get_running_loop()
