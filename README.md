#Python Ricing
A little experiment with high speed python microservices, based on FastAPI's architecture.

Using uvicorn as a high speed HTTP server using uvloop and ASGI.

Using Starlette as a high speed ASGI framework

Using Redis or postgresql to sync threads and containers to advance counter state and halt at 100. 
  * Redis should be faster, but is not perfectly consistant (in an ACID sense), so it is possible that the counter could advance past 100.
  * Postgres will be slower, but will have no race conditions

Everything is deployed with OCI containers and Kubernetes manifests, which can be run with podman.
