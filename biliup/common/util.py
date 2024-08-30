import asyncio

import httpx


TIMEOUT = httpx.Timeout(
    timeout=15.0,
    connect=15.0,
    pool=60.0,
)
LIMITS = httpx.Limits(
    max_connections=100,
    max_keepalive_connections=20,
    keepalive_expiry=30.0
)

client = httpx.AsyncClient(
    http2=True,
    follow_redirects=True,
    timeout=TIMEOUT,
    limits=LIMITS
)

loop = asyncio.get_running_loop()
