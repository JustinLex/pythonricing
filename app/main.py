import asyncio

from starlette.applications import Starlette
from starlette.responses import JSONResponse, Response
from starlette.routing import Route
from starlette.requests import Request

from loguru import logger


import redis.asyncio as redis

from .logs import init_logger


# Set up loguru and inject it so that it intercepts all stdlib and uvicorn logging
init_logger()


# Our one and only Route
async def homepage(request: Request) -> Response:

    # Log current request number
    # Using loguru kwargs to add the "request_count" key-value to the "extra" dict in the JSON log line
    logger.info("Request #{request_count}", request_count=0)

    return JSONResponse({'hello': 'world'})


# Starlette entrypoint
app = Starlette(debug=True, routes=[
    Route('/', homepage),
])


# Connect to redis once Starlette has started
@app.on_event("startup")
async def connect_redis() -> None:
    connection = redis.Redis(host="127.0.0.1", port=6379)
    ping_success = connection.ping()
    logger.info("Ping successful: {ping_success}", ping_success=ping_success)
    await connection.close()
