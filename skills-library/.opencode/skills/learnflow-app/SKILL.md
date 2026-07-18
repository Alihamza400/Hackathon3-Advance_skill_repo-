---
name: learnflow-ai
description: Deploy and manage the LearnFlow AI learning platform with multi-agent workflows
---

# LearnFlow AI Skill

## When to Use
- Deploy AI-powered education platform
- Manage multi-agent workflows for personalized learning
- Integrate LLMs for assessment generation and content creation

## Instructions
1. Bootstrap platform: `./scripts/bootstrap_platform.sh`
2. Deploy services: `./scripts/deploy_services.sh`
3. Configure autoscaling: `./scripts/configure_autoscaling.sh`
4. Verify health: `./scripts/verify_health.sh`

## Validation
- [ ] All services are running
- [ ] Platform health endpoint returns 200
- [ ] AI agents can access platform APIs

See REFERENCE.md for deeper documentation.