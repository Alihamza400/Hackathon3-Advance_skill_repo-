---
name: docusaurus-deploy
description: Deploy Docusaurus documentation sites with Kubernetes
---

# Docusaurus Kubernetes Deployment Skill

## When to Use
- Building technical documentation sites
- Need scalable documentation platforms
- Require version control for documentation
- Want embedded search functionality

## Instructions
1. Create Docusaurus config: `./scripts/create_docusaurus.sh <doc-name>`
2. Configure deployment: `./scripts/configure_docusaurus.sh <doc-name>`
3. Build static site: `./scripts/build_docusaurus.sh <doc-name>`
4. Deploy to K8s: `./scripts/deploy_docusaurus.sh <doc-name>`
5. Configure search: `./scripts/configure_search.sh <doc-name>`
6. Verify deployment: `./scripts/verify_docusaurus.sh <doc-name>`

## Validation
- [ ] Documentation site built successfully
- [ ] Kubernetes deployment running
- [ ] Search functionality configured
- [ ] Ingress route traffic correctly
- [ ] Accessibility standards met

See [REFERENCE.md](./REFERENCE.md) for Docusaurus deployment configurations.
