import asyncio

import httpx


TIMEOUT = httpx.Timeout(
    timeout=120.0,
    connect=15.0,
    pool=35.0
)
LIMITS = httpx.Limits(
    max_connections=1000,
    max_keepalive_connections=100,
    keepalive_expiry=35.0 # 大于 event_loop_interval 以尽可能复用连接
)

client = httpx.AsyncClient(
    http2=True,
    follow_redirects=True,
    timeout=TIMEOUT,
    limits=LIMITS
)

loop = asyncio.get_running_loop()
