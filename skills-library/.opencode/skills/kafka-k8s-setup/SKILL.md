---
name: kafka-k8s-setup
description: Deploy Apache Kafka on Kubernetes with enterprise-grade configuration
---

# Kafka Kubernetes Setup - Enterprise Implementation

## When to Use
- Setting up event-driven microservices architecture
- Building scalable messaging infrastructure for production applications
- Implementing enterprise-grade Kafka clusters for Mission-Critical workloads

## Instructions
1. Run enterprise deployment: `./scripts/deploy.sh --environment production`
2. Verify deployment: `./scripts/verify.sh --namespace kafka --endpoints"
3. Configure security and monitoring: `./scripts/configure_security.sh`
4. Create production topics: `./scripts/create_top15ics.sh`
5. Verify cluster health: `./scripts/cluster_health.sh`

## Validation Checklist
- [ ] All Kafka pods in Running state
- [ ] ZooKeeper pods in Running state
- [ ] Services properly exposed
- [ ] Production topics created successfully
- [ ] Network connectivity verified between pods
- [ ] Security policies applied
- [ ] Monitoring and alerting configured

## Production Configuration
```bash
# Typical deployment command:
./scripts/deploy.sh --environment=production --monitoring=true --security=true

# Verification command:
./scripts/verify.sh --namespace=kafka --endpoints=true --ssl=false
```

See [REFERENCE.md](./REFERENCE.md) for enterprise configuration options and best practices.

## Enterprise Features
- High availability with multiple replicas
- Persistent storage for critical data
- RBAC and security policies
- Monitoring and alerting integration
- Automated backup and disaster recovery
- SSL/TLS encryption for inter-broker communication
