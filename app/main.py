import asyncio
from typing import Optional

from starlette.applications import Starlette
from starlette.responses import JSONResponse, Response
from starlette.routing import Route
from starlette.requests import Request

from loguru import logger

import redis.asyncio as redis

from .logs import init_logger


# Connection object for redis
redis_conn: Optional[redis.Redis] = None


# Set up loguru and inject it so that it intercepts all stdlib and uvicorn logging
init_logger()


# Our one and only Route
async def homepage(request: Request) -> Response:

    # Get current count if exists
    redis_request_count: Optional[str] = await redis_conn.get('request_count')

    # convert redis_request_count to int
    if redis_request_count is None:  # Initialize counter if we were the first ones here
        request_count: int = 0
    else:
        request_count: int = int(redis_request_count)

    # Normal operation, first 100 requests. Update counter asap, Log and response.
    if request_count < 100:
        request_count += 1
        await redis_conn.set('request_count', str(request_count))

        # Log current request number
        # Using loguru kwargs to add the "request_count" key-value to the "extra" dict in the JSON log line
        logger.info("Request #{request_count}", request_count=request_count)

        return JSONResponse({
            'hello': 'world',
            'request_num': request_count,
        })

    # We already hit 100 requests, log and response
    else:
        logger.warning("Received a request but we already hit 100 requests!")

        return JSONResponse({
            'Go': 'away!',
            'request_num': request_count,
        })


# Starlette entrypoint
app = Starlette(debug=True, routes=[
    Route('/', homepage),
])


# Connect to redis once Starlette has started
# (Also ensures redis server is running before we handle requests)
@app.on_event("startup")
async def connect_redis() -> None:
    global redis_conn
    await asyncio.sleep(5)  # sleep 5 secs so redis can start, since dead threads don't respawn when using multiple workers
    redis_conn = redis.Redis(host="127.0.0.1", port=6379)
    ping_success = await redis_conn.ping()
    logger.info("Redis ping successful: {ping_success}", ping_success=ping_success)


# Disconnect from redis when Starlette shuts down
@app.on_event("shutdown")
async def disconnect_redis() -> None:
    await redis_conn.close()
