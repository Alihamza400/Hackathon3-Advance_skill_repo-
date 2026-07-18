# LearnFlow AI Skill

A reusable skill to deploy and manage the LearnFlow AI learning platform using Helm, Docker, and Kubernetes best practices.

## Quick Start

```bash
# Bootstrap environment and build Docker image
./scripts/bootstrap_platform.sh

# Deploy the service
./scripts/deploy_services.sh

# Configure autoscaling
./scripts/configure_autoscaling.sh

# Verify health endpoint
./scripts/verify_health.sh
```

## Scripts

| Script | Purpose |
|--------|---------|
| `bootstrap_platform.sh` | Create virtual environment, install dependencies, build Docker image |
| `deploy_services.sh` | Build and push Docker image, Helm install release |
| `configure_autoscaling.sh` | Apply Horizontal Pod Autoscaler |
| `verify_health.sh` | Curl `/health` endpoint and expect 200 OK |
| `verify_deployment.sh` | (future) Verify Helm release status and test hooks |

## Helm Chart

The chart is located at `~/infra/learnflow-app/helm/learnflow-app/`.  
Key values files:

- `values.yaml` – default configuration
- `values-production.yaml` – production‑ready settings

Install with:

```bash
helm install learnflow-app ./infra/learnflow-app/helm/learnflow-app -f ./infra/learnflow-app/helm/learnflow-app/values-production.yaml
```

Uninstall with:

```bash
helm uninstall learnflow-app
```

## Validation

- Health check returns **200**.
- HPA scales based on CPU and memory.
- Tests run via Helm test hook.

See `AGENTS.md` for enterprise standards.