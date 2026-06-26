## Week 5 — GitHub Actions CI Pipeline

### Pipeline overview

```
git push to main
  ├── Job 1: Bandit Python security scan (parallel)
  ├── Job 2: pytest — 6 tests (parallel)
  └── Job 3: Build + Trivy scan + Push to ghcr.io (after 1 & 2 pass)
```

### What runs on every push

- **Bandit** — static security analysis of Python code
- **pytest** — 6 tests covering all Flask endpoints
- **Docker build** — using `python:3.11-slim` with non-root user
- **Trivy** — CVE scan of built image (CRITICAL + HIGH severity)
- **Push** — three tags to GitHub Container Registry

### Image location

```
ghcr.io/manishaacharya111/production-devops-platform:latest
ghcr.io/manishaacharya111/production-devops-platform:main
ghcr.io/manishaacharya111/production-devops-platform:sha-<commit>
```

### Pull the image

```bash
docker pull ghcr.io/manishaacharya111/production-devops-platform:latest
```

### CVE fix applied

Upgraded `gunicorn 21.2.0` → `22.0.0` to fix CVE-2024-1135 (HTTP Request Smuggling) detected by Trivy during first pipeline run.

### Flask app endpoints

| Endpoint | Purpose |
|---|---|
| `/` | Returns service info — used by load balancer health checks |
| `/health` | Kubernetes liveness/readiness probe target |
| `/metrics` | Prometheus scrape endpoint — exposes RED metrics |
| `/error` | Simulates 500 error — used for incident simulation in week 9 |

## Week 6 — Helm Chart + ArgoCD GitOps

### What was built

A complete GitOps deployment pipeline — code pushed to GitHub automatically deploys to Kubernetes via ArgoCD with zero manual kubectl commands.

### Helm chart structure

```
helm/flask-app/
  Chart.yaml              # chart metadata
  values.yaml             # default configuration
  templates/
    deployment.yaml       # Flask app deployment with liveness/readiness probes
    service.yaml          # ClusterIP service routing to port 5000
    ingress.yaml          # nginx Ingress routing flask-app.local
    networkpolicy.yaml    # allow ingress-nginx → flask-app on port 5000
```

### ArgoCD setup

- Installed via `kubectl apply -f install.yaml` into `argocd` namespace
- Application watches `helm/flask-app/` in this repo
- Auto-sync enabled — every Git push syncs to cluster within 3 minutes
- selfHeal enabled — manual kubectl changes are reverted automatically

### GitOps flow

```
git push
  → ArgoCD detects commit
    → renders Helm chart
      → applies changes to cluster
        → app updated with zero manual steps
```

### Access the app locally

```bash
# Start port-forwards (two terminals)
kubectl port-forward svc/argocd-server -n argocd 9443:443
kubectl port-forward -n ingress-nginx service/ingress-nginx-controller 8081:80

# Test endpoints
curl -H "Host: flask-app.local" http://localhost:8081/
curl -H "Host: flask-app.local" http://localhost:8081/health
curl -H "Host: flask-app.local" http://localhost:8081/metrics
```

### Key debugging story — NetworkPolicy blocking traffic

Pod was Running and endpoints were populated, but requests timed out.

**Root cause:** `default-deny-all` NetworkPolicy from week 2 labs was blocking all pod-to-pod traffic including ingress-nginx → flask-app.

**Discovery:** `port-forward` to pod worked but `busybox wget` to pod IP timed out. Port-forward bypasses network policies (goes through kubectl API server, not pod network). Pod-to-pod test reveals real network path.

**Fix:** Added `networkpolicy.yaml` to Helm chart allowing ingress-nginx namespace to reach flask-app on port 5000. Pushed to Git → ArgoCD synced automatically → app reachable.
