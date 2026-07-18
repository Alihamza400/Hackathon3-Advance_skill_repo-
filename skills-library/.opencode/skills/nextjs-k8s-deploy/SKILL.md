---
name: nextjs-k8s-deploy
description: Deploy Next.js applications with Kubernetes using Helm
---

# Next.js Kubernetes Deployment Skill

## When to Use
- Building frontend applications with Next.js
- Need containerized web applications
- Require scaling and management with Kubernetes
- Want to deploy complex frontend applications

## Instructions
1. Create Next.js configuration: `./scripts/create_config.sh <app-name>`
2. Build Docker image: `./scripts/build_image.sh <app-name>`
3. Create Helm chart: `./scripts/create_helm.sh <app-name>`
4. Deploy to K8s: `./scripts/deploy_helm.sh <app-name>`
5. Configure ingress: `./scripts/setup_ingress.sh <app-name>`
6. Verify deployment: `./scripts/verify_helm.sh <app-name>`

## Validation
- [ ] Docker image built successfully
- [ ] Helm chart configured correctly
- [ ] Deployment running in Kubernetes
- [ ] Ingress routed traffic properly
- [ ] Application health checks passing

See [REFERENCE.md](./REFERENCE.md) for Next.js deployment best practices.
