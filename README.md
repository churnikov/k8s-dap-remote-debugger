# k8s-remote-debugger

Minimal FastAPI app packaged for local Kubernetes deployment with Helm.

The chart also starts two Celery worker containers:

- `worker-default`, consuming the `default` queue for `tasks.echo`
- `worker-math`, consuming the `math` queue for `tasks.add`

Redis runs as an in-pod broker by default.

## Run locally with Python

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## Build the container images

```bash
docker build -t k8s-remote-debugger:local .
docker build -f Dockerfile.worker \
  --build-arg CELERY_WORKER_QUEUE=default \
  --build-arg CELERY_WORKER_NAME=worker-default \
  -t k8s-remote-debugger-worker-default:local .
docker build -f Dockerfile.worker \
  --build-arg CELERY_WORKER_QUEUE=math \
  --build-arg CELERY_WORKER_NAME=worker-math \
  -t k8s-remote-debugger-worker-math:local .
```

## Deploy with Helm

The Helm chart is in `chart/`. Rancher Desktop is the only supported local Kubernetes runtime, and it expects the image to already exist inside that runtime.

### Rancher Desktop

First confirm your Kubernetes context:

```bash
kubectl config current-context
```

It should usually be `rancher-desktop`.

If Rancher Desktop is using the `containerd` engine, build the image into the `k8s.io` namespace so Kubernetes can see it:

```bash
nerdctl --namespace k8s.io build -t k8s-remote-debugger:local .
nerdctl --namespace k8s.io build -f Dockerfile.worker \
  --build-arg CELERY_WORKER_QUEUE=default \
  --build-arg CELERY_WORKER_NAME=worker-default \
  -t k8s-remote-debugger-worker-default:local .
nerdctl --namespace k8s.io build -f Dockerfile.worker \
  --build-arg CELERY_WORKER_QUEUE=math \
  --build-arg CELERY_WORKER_NAME=worker-math \
  -t k8s-remote-debugger-worker-math:local .
helm upgrade --install k8s-remote-debugger ./chart
```

If Rancher Desktop is using the `dockerd (moby)` engine, build it with Docker:

```bash
docker build -t k8s-remote-debugger:local .
docker build -f Dockerfile.worker \
  --build-arg CELERY_WORKER_QUEUE=default \
  --build-arg CELERY_WORKER_NAME=worker-default \
  -t k8s-remote-debugger-worker-default:local .
docker build -f Dockerfile.worker \
  --build-arg CELERY_WORKER_QUEUE=math \
  --build-arg CELERY_WORKER_NAME=worker-math \
  -t k8s-remote-debugger-worker-math:local .
helm upgrade --install k8s-remote-debugger ./chart
```

## Customize values

Override the image or service settings at install time:

```bash
helm upgrade --install k8s-remote-debugger ./chart \
  --set image.repository=k8s-remote-debugger \
  --set image.tag=local \
  --set image.pullPolicy=Never \
  --set workers[0].image.repository=k8s-remote-debugger-worker-default \
  --set workers[1].image.repository=k8s-remote-debugger-worker-math
```

API debugging is enabled by default and exposes `debugpy` on port `5678`. Worker debugging is also enabled by default:

- `worker-default`: `5679`
- `worker-math`: `5680`

If you want the API container to pause until your debugger attaches:

```bash
helm upgrade --install k8s-remote-debugger ./chart \
  --set debug.waitForClient=true
```

Worker containers can pause the same way:

```bash
helm upgrade --install k8s-remote-debugger ./chart \
  --set workers[0].debug.waitForClient=true \
  --set workers[1].debug.waitForClient=true
```

## Access the app

```bash
kubectl port-forward service/k8s-remote-debugger 8000:8000 5678:5678 5679:5679 5680:5680
```

Then open:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/healthz`
- `http://127.0.0.1:8000/hello/User`
- API `debugpy` on `127.0.0.1:5678`
- `worker-default` `debugpy` on `127.0.0.1:5679`
- `worker-math` `debugpy` on `127.0.0.1:5680`

Queue a task and fetch its result:

```bash
curl -X POST http://127.0.0.1:8000/tasks/echo \
  -H 'content-type: application/json' \
  -d '{"message":"hello celery"}'

curl -X POST http://127.0.0.1:8000/tasks/add \
  -H 'content-type: application/json' \
  -d '{"left":2,"right":3}'

curl http://127.0.0.1:8000/tasks/<task-id>
```
