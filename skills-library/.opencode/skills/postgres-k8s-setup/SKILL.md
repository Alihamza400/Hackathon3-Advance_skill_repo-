---
name: postgres-k8s-setup-enterprise
name: postgres-k8s-setup
description: Deploy production-grade PostgreSQL on Kubernetes with enterprise features
---

# PostgreSQL Kubernetes Setup - Enterprise Implementation

## When to Use
- Building production databases for mission-critical applications
- Implementing high-availability database infrastructure
- Setting up PostgreSQL with enterprise-grade security and backup
- Creating distributed PostgreSQL clusters for enterprise workloads

## Instructions
1. Run production deployment: `./scripts/deploy.sh --environment production --ha-enabled --backup-enabled`
2. Apply enterprise configuration: `./scripts/configure.py --ssl enabled --replication enabled`
3. Run initial migration: `./scripts/run_migrations.py --data-migration true --consistency-check true`
4. Verify deployment: `./scripts/verify.py --health-check comprehensive`
5. Configure backup strategy: `./scripts/configure_backups.sh --sla critical`

## Validation Checklist
- [ ] All PostgreSQL pods in Running state
- [ ] High availability cluster verified (minimum 3 replicas)
- [ ] SSL/TLS encryption configured
- [ ] Replication and streaming enabled
- [ ] Enterprise backup and recovery configured
- [ ] Monitoring and observability set up
- [ ] Security policies and RBAC applied
- [ ] Performance tuning applied
- [ ] Data migration completed successfully
- [ ] Consistency and redundancy verified

## Enterprise Configuration
```bash
# Production deployment command:
./scripts/deploy.sh --environment=production --ha-enabled=true --backup-enabled=true --ssl=true --monitoring=true

# Verification command:
./scripts/verify.py --health-check=comprehensive --backup-check=true --replication-check=true
```

See [REFERENCE.md](./REFERENCE.md) for enterprise PostgreSQL setup requirements and best practices.

## Enterprise Features
- Multi-zone high availability with minimum 3 node cluster
- Persistent storage with enterprise-class storage classes (gp3, io1)
- SSL/TLS encryption for all data in transit
- Streaming replication for zero-downtime maintenance
- Automated backup and point-in-time recovery
- Comprehensive monitoring and alerting integration
- Advanced security policies and role-based access control
- Performance optimization for enterprise workloads
- Automated failover and disaster recovery
- Data consistency guarantees

## Backup and Disaster Recovery
- Local volume backups with retention policies
- Remote storage integration (S3, GCS, Azure)
- Automated backup scheduling with SLA compliance
- Point-in-time recovery with RPO/RTO optimization
