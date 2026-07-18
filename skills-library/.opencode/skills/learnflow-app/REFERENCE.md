# LearnFlow AI Skill – Reference Documentation

## Overview
This skill deploys the LearnFlow AI learning platform using Helm, Docker, and Kubernetes. It provides scripts for bootstrapping, deployment, autoscaling, and health verification.

## Chart Content
- `Chart.yaml`: Chart metadata
- `values.yaml`: Default configuration
- `values-production.yaml`: Production‑ready settings
- `templates/`: Helm manifests for Deployment, Service, Ingress, HPA, and test hook
- `templates/tests/test-connection.yaml`: Validates the health endpoint post‑install

## Scripts
| Script | Purpose |
|--------|---------|
| `bootstrap_platform.sh` | Creates a Python venv, installs FastAPI & Uvicorn, builds Docker image |
| `deploy_services.sh` | Builds and pushes Docker image, reads Helm values for deployment |
| `configure_autoscaling.sh` | Applies a Horizontal Pod Autoscaler based on CPU utilization |
| `verify_health.sh` | Calls `/health` and expects a 200 response |
| `verify_deployment.sh` | Confirms Helm release status and runs the test hook |

## Values Overview
- `replicaCount`: Default 1; can be overridden via `values-production.yaml`
- `image.repository`: `learnflow-app`
- `image.tag`: `latest`
- `service.port`: `8000`
- `autoscaling` settings for CPU and memory thresholds
- `ingress.hosts` defines the external domain and paths

## Testing
- Helm test hook (`templates/tests/test-connection.yaml`) performs a `wget`‑based health check.
- CI workflow (`.github/workflows/ci.yml`) runs linting, unit tests, and Helm linting on each push.

## Quick Start
```bash
# Bootstrap and deploy locally (requires Docker, Helm, kubectl)
./skills-library/.opencode/skills/learnflow-app/scripts/bootstrap_platform.sh
./skills-library/.opencode/skills/learnflow-app/scripts/deploy_services.sh
./skills-library/.opencode/skills/learnflow-app/scripts/configure_autoscaling.sh
./skills-library/.opencode/skills/learnflow-app/scripts/verify_health.sh
```