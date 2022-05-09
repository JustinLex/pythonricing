#Python Ricing
A little experiment with high speed python microservices, based on FastAPI's architecture.

## Library decisions

### HTTP framework
Using uvicorn as a high speed HTTP server using uvloop and ASGI.

Using Starlette as a high speed ASGI framework

### Database / Thread syncing
Using Redis or postgresql to sync threads and containers to advance counter state and halt at 100. 
  * Redis should be faster, but is not perfectly consistant (in an ACID sense), so it is possible that the counter could advance past 100.
  * Postgres will be slower, but will have no race conditions

###Logging
Logging was going to be done with Sentry, which was the best option for logging monolithic apps back in the 2010s, 
but with microservices running in kubernetes, 
[it's best to just log raw json to stdout](https://kubernetes.io/docs/concepts/cluster-administration/logging/).
See [this](https://gitlab.com/stephen6/jslog4kube) for another python project that has the same idea.

Therefore, to enable these best-practices, it was decided to use Loguru for fast, async, and JSONized logging.
Inspiration came from nsidnev's amazing "[FastAPI real-world example app](https://github.com/nsidnev/fastapi-realworld-example-app)",
which introduced me to Loguru, and has some great code for injecting Loguru into the uvicorn logger. 
Check out this example app if you want to see some proper production-ready python code. 
(Though their app isn't as well containerized and Kubernetes-ready as this app is!)

### Operations
Everything is deployed with OCI containers and Kubernetes manifests, which can be run with podman.

## OCI container image size
It's a bit tricky to make small python container images, as there are a lot of runtime libraries needed.

Using an python-alpine base image, the app image comes out at 65MB.

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
The application is now available at `127.0.0.1:8080`, you can access it in your browser or use benchmarking tools

### Tear down pods
```commandline
podman play kube --down playfile.yaml
```

