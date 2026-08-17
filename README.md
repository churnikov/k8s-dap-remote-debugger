# k8s-remote-debugger

Minimal FastAPI app packaged for local Kubernetes deployment with Helm.

## Run locally with Python

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## Build the container image

```bash
docker build -t k8s-remote-debugger:local .
```

## Deploy with Helm

The Helm chart is in `chart/`. It expects the image to already exist inside your local cluster runtime.

### Rancher Desktop

First confirm your Kubernetes context:

```bash
kubectl config current-context
```

It should usually be `rancher-desktop`.

If Rancher Desktop is using the `containerd` engine, build the image into the `k8s.io` namespace so Kubernetes can see it:

```bash
nerdctl --namespace k8s.io build -t k8s-remote-debugger:local .
helm upgrade --install k8s-remote-debugger ./chart
```

If Rancher Desktop is using the `dockerd (moby)` engine, build it with Docker:

```bash
docker build -t k8s-remote-debugger:local .
helm upgrade --install k8s-remote-debugger ./chart
```

### kind

```bash
kind load docker-image k8s-remote-debugger:local
helm upgrade --install k8s-remote-debugger ./chart
```

### minikube

```bash
minikube image load k8s-remote-debugger:local
helm upgrade --install k8s-remote-debugger ./chart
```

## Customize values

Override the image or service settings at install time:

```bash
helm upgrade --install k8s-remote-debugger ./chart \
  --set image.repository=k8s-remote-debugger \
  --set image.tag=local \
  --set image.pullPolicy=Never
```

Debugging is enabled by default and exposes `debugpy` on port `5678`. If you want the pod to pause until your debugger attaches:

```bash
helm upgrade --install k8s-remote-debugger ./chart \
  --set debug.waitForClient=true
```

## Access the app

```bash
kubectl port-forward service/k8s-remote-debugger 8000:8000 5678:5678
```

Then open:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/healthz`
- `http://127.0.0.1:8000/hello/User`
- `debugpy` on `127.0.0.1:5678`
