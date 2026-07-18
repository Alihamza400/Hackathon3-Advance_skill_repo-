---
name: fastapi-dapr-agent
description: Create FastAPI microservices with Dapr sidecars for AI tutoring
---

# FastAPI + Dapr AI Agent Service

## When to Use
- Building AI tutoring microservices for LearnFlow
- Need stateful, event-driven backend services
- Require Dapr for distributed system patterns

## Instructions
1. Create service template: `./scripts/create_service.sh <service-name>`
2. Configure Dapr components: `./scripts/configure_dapr.sh <service-name>`
3. Deploy with Helm: `./scripts/deploy_service.sh <service-name>`
4. Verify status: `python scripts/verify.py <service-name>`
5. Test functionality: `./scripts/test_service.sh <service-name>`

## Validation
- [ ] Dapr sidecar running
- [ ] Service health checks passing
- [ ] Pub/Sub messaging configured
- [ ] State management working

See [REFERENCE.md](./REFERENCE.md) for component templates and configurations.
