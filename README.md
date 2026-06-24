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