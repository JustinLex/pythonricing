import logging

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from loguru import logger

from .logs import init_logger


# Set up loguru and inject it so that it intercepts all stdlib and uvicorn logging
init_logger()


# Our one and only Route
async def homepage(request):
    logger.info("logurulog")
    logging.getLogger("uvicorn.access").info("uvicornlog")
    return JSONResponse({'hello': 'world'})


# Starlette entrypoint
app = Starlette(debug=True, routes=[
    Route('/', homepage),
])
