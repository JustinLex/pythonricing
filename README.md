# Python Ricing
A little experiment with high speed python microservices, based on FastAPI's architecture.

## Library decisions

### HTTP framework
* Using uvicorn as a high speed HTTP server using uvloop and ASGI.
* Using Starlette as a high speed ASGI framework
  * Starlette is probably our biggest bottleneck for such a small benchmark like this, 
  but it's probably the best balance of speed and usability for a real-world microservice.

### Database / Thread syncing
Using Redis or postgresql to sync threads and containers to advance counter state and halt at 100. 
  * Redis should be faster, but is not perfectly consistant at scale (in an ACID sense), 
so it is possible that numbers in the count could be repeated.
  * Postgres will be slower, but will have no race conditions

### Logging
Logging was going to be done with Sentry, which was the best option for logging monolithic apps back in the 2010s, 
but with microservices running in kubernetes, 
[it's best to just log raw json to stdout](https://kubernetes.io/docs/concepts/cluster-administration/logging/).
See [this](https://gitlab.com/stephen6/jslog4kube) for another python project that has the same idea.

Therefore, to enable these best-practices, it was decided to use Loguru for fast, async, and JSONized logging.
Inspiration came from nsidnev's amazing "[FastAPI real-world example app](https://github.com/nsidnev/fastapi-realworld-example-app)",
which introduced me to Loguru, and has some great code for injecting Loguru into the uvicorn logger. 
Check out their example app if you want to see some proper production-ready python code. 
(Though their app isn't as well containerized and Kubernetes-ready as this app is!)

Note: Even though loguru is supposed to be asynchronous, it still seems to generate an entire millisecond of latency per request.
It's possible that loguru is not asynchronous when logging to stdout.

### Operations
Everything is deployed with OCI containers and Kubernetes manifests, which can be run with podman.

Ideally we would use 16 containers and load-balance them for my 16 thread laptop, 
but podman does not have built-in support for service load balancing like real Kubernetes,
so we tell uvicorn to spawn 16 workers instead.
This is more fragile for production, but it works well enough for some benchmarking.

The Containerfile for the application (aka Dockerfile) can be found at `./Containerfile`.

The Kubernetes manifest for deploying the application pods and database pods is at `./playfile.yaml`.

## OCI container image size
It's a bit tricky to make small python container images, as there are a lot of runtime libraries needed.

Using a python-alpine base image, the app image comes out at 65.8MB.

## Testing app standalone

### Build app
```commandline
podman build -t pythonricing .
```

### Start pods
```commandline
podman play kube playfile.yaml
```

### Make requests
The application is now available at `127.0.0.1:8080`, you can access it in your browser or use benchmarking tools.

You can watch the request numbers update with this command:
```commandline
watch -n 0.1 'podman logs pythonricing-pythonricing_container 2> /dev/null | tail -n 20 | jq .record.extra.request_count'
```

### Tear down pods
```commandline
podman play kube --down playfile.yaml
```

Sometimes, if a pod fails to start, `podman play` will refuse to work, and you will have to delete the pods manually.
```commandline
podman pod rm pythonricing -f
podman pod rm redis -f
```

## Benchmarks

### Low-load benchmark
Benchmarked with Apache benchmark: `ab -n 10000 -c 10 http://127.0.0.1:8080/`

Time per request:

16 threads with Redis syncing: 3761 requests/s, and 2.659 ms per request

16 threads with no syncing: 4375 requests/s, and 2.285ms per request

16 threads with loguru disabled: 6013 requests/s, and 1.663ms per request

16 threads with Redis syncing and C-based libraries: 5834 requests/s, and 1.714 ms per request

16 threads with loguru disabled and C-based libraries: 10409 requests/s, and 0.961 ms per request


### High-load benchmark
Benchmarked with Apache benchmark: `ab -n 100000 -c 1000 http://127.0.0.1:8080/`

16 threads with redis syncing: 6384 requests/s, and 156.546ms per request

16 threads with loguru disabled: 6808 requests/s, and 146.879ms per request

16 threads with C-based libraries: 7229 requests/s, and 138.316 ms per request

16 threads with C-based libraries and loguru disabled: 10590 requests/s, and 94.423 ms per request
