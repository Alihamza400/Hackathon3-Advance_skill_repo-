# PostgreSQL Kubernetes Setup - Enterprise Reference

## Overview

This skill provides enterprise-grade PostgreSQL deployment on Kubernetes with high availability, automated backup, point-in-time recovery, and comprehensive monitoring. Designed for mission-critical applications requiring zero-downtime deployments and regulatory compliance.

## Architecture

### High Availability Topology

```
                    ┌─────────────────────────────────────────┐
                    │         PostgreSQL HA Cluster             │
                    │  ┌─────────────┐    ┌─────────────┐      │
                    │  │   Primary   │◄───│  Replica 1  │      │
                    │  │  (Writer)   │    │  (Reader)   │      │
                    │  └─────────────┘    └─────────────┘      │
                    │         │                   │             │
                    │         ▼                   ▼             │
                    │  ┌─────────────┐    ┌─────────────┐      │
                    │  │   Replica 2 │    │  Replica 3  │      │
                    │  │  (Reader)   │    │  (Standby)  │      │
                    │  └─────────────┘    └─────────────┘      │
                    └─────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
            ┌───────────────┐   ┌───────────────┐
            │   Backup      │   │  Monitoring   │
            │ (S3/GCS/Azure)│   │ (Prometheus)  │
            └───────────────┘   └───────────────┘
```

### Component Specifications

| Component | Specification |
|-----------|---------------|
| **Primary** | 1 Writer, Read-Write |
| **Replicas** | 2+ Readers (Async/Sync replication) |
| **Storage** | 50Gi gp3 (Primary), 50Gi gp3 (Replicas) |
| **Replication** | Streaming (WAL shipping) |
| **Failover** | Automatic via Patroni/repmgr |
| **Backup** | pgBackRest to S3/GCS/Azure Blob |
| **PITR** | Point-in-Time Recovery to any second |

## Deployment Modes

### Development
```bash
./scripts/deploy.sh --environment=development
```
- Single instance, no HA
- Local storage, no backup
- Minimal resources (100m CPU, 256Mi memory)

### Staging
```bash
./scripts/deploy.sh --environment=staging --ha-enabled=true
```
- 2 replicas (1 Primary + 1 Replica)
- Basic monitoring
- Daily backups to local storage

### Production
```bash
./scripts/deploy.sh \
  --environment=production \
  --ha-enabled=true \
  --backup-enabled=true \
  --ssl=true \
  --monitoring=true
```
- 3+ replicas (1 Primary + 2+ Sync replicas)
- Synchronous replication (zero data loss)
- Automated backup to S3/GCS with encryption
- Full TLS/SSL encryption
- Full Prometheus/Grafana monitoring
- Automated failover with Patroni
- pgBackRest to S3/GCS with retention policies

## Database Architecture

### Schema Design Standards

```sql
-- Naming conventions
CREATE TABLE user_accounts (          -- snake_case table names
    id              BIGSERIAL PRIMARY KEY,
    email           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ        -- soft delete
);

-- Indexes follow naming convention
CREATE INDEX idx_user_accounts_email ON user_accounts(email);
CREATE INDEX idx_user_accounts_created_at ON user_accounts(created_at);

-- Triggers for updated_at
CREATE TRIGGER update_user_accounts_updated_at
    BEFORE UPDATE ON user_accounts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### Partitioning Strategy

```sql
-- Time-based partitioning for large tables
CREATE TABLE audit_logs (
    id          BIGSERIAL,
    user_id     BIGINT NOT NULL,
    action      VARCHAR(100) NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
) PARTITION BY RANGE (created_at);

-- Monthly partitions
CREATE TABLE audit_logs_2024_01 PARTITION OF audit_logs
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

## Security Configuration

### SSL/TLS Encryption

```bash
# Enable TLS for all connections
./scripts/deploy.sh --ssl=true
```

**Configuration:**
- Server certificate: Auto-generated via cert-manager
- Client certificate verification: Required for admin connections
- Cipher suites: TLS 1.2+, ECDHE-RSA-AES256-GCM-SHA384
- Certificate rotation: Automatic via cert-manager (90 days)

### Authentication & Authorization

```sql
-- Role-based access control
CREATE ROLE readonly_user NOLOGIN;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;

CREATE ROLE app_user NOLOGIN;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;

CREATE ROLE admin_user NOLOGIN;
GRANT ALL PRIVILEGES ON DATABASE app_db TO admin_user;
```

### Row Level Security (RLS)

```sql
-- Enable RLS for multi-tenant isolation
ALTER TABLE user_data ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON user_data
    FOR ALL TO app_user
    USING (tenant_id = current_setting('app.current_tenant')::uuid);
```

## Backup & Disaster Recovery

### Backup Strategy (pgBackRest)

```yaml
# Backup configuration
backup:
  type: full           # Full + incremental
  schedule: "0 2 * * *"  # Daily at 2 AM
  retention:
    full: 30           # Keep 30 full backups
    diff: 7            # Keep 7 differential backups
  repository:
    type: s3
    bucket: enterprise-db-backups
    region: us-east-1
    encryption: aes256
```

### Recovery Procedures

#### Point-in-Time Recovery (PITR)
```bash
# Recover to specific timestamp
./scripts/recover.sh \
  --target-time="2024-01-15 14:30:00" \
  --target-db=production

# Recovery validation
./scripts/validate_recovery.sh --target-db=production
```

#### Cross-Region Failover
```bash
# Promote standby to primary
./scripts/failover.sh --target-cluster=dr-cluster

# Verify promotion
./scripts/verify_failover.sh --target-db=production
```

### Recovery Point/Time Objectives

| Tier | RPO | RTO | Backup Frequency |
|------|-----|-----|------------------|
| Critical | < 1 sec | < 5 min | Continuous (sync replication) |
| Standard | 1 hour | 30 min | Hourly incremental |
| Archive | 24 hours | 4 hours | Daily full |

## Monitoring & Alerting

### Key Metrics

| Metric | Threshold | Alert |
|--------|-----------|-------|
| `pg_up` | = 0 | Critical - Instance down |
| `pg_replication_lag` | > 1GB | Warning - Replication lag |
| `pg_database_size_bytes` | > 80% capacity | Warning - Disk space |
| `pg_stat_activity_count` | > 80% max_connections | Warning - Connection pool |
| `pg_backup_last_success_timestamp` | > 26 hours | Critical - Backup failed |

### Grafana Dashboards
- **PostgreSQL Overview**: Connections, throughput, latency
- **Replication Status**: Lag, sync status, replica health
- **Backup Status**: Last backup, size, duration, success rate
- **Performance**: Query latency, cache hit ratio, deadlocks

### Critical Alerts

```yaml
# PostgreSQL Down
- alert: PostgresDown
  expr: pg_up == 0
  for: 1m
  labels:
    severity: critical
  annotations:
    summary: "PostgreSQL instance {{ $labels.instance }} is down"

# Replication Lag
- alert: PostgresReplicationLag
  expr: pg_replication_lag > 1073741824  # 1GB
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Replication lag on {{ $labels.instance }} is {{ $value | humanize }}B"

# Backup Failure
- alert: PostgresBackupFailed
  expr: time() - pg_backup_last_success_timestamp > 90000
  labels:
    severity: critical
  annotations:
    summary: "PostgreSQL backup failed for {{ $labels.instance }}"
```

## Performance Tuning

### PostgreSQL Configuration (postgresql.conf)

```properties
# Memory
shared_buffers = 25% of RAM (e.g., 4GB for 16GB)
effective_cache_size = 75% of RAM
work_mem = 32MB
maintenance_work_mem = 512MB

# WAL
wal_level = replica
max_wal_senders = 10
wal_keep_segments = 64
wal_compression = on

# Checkpointing
checkpoint_timeout = 15min
max_wal_size = 4GB
min_wal_size = 1GB
checkpoint_completion_target = 0.9

# Parallelism
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
parallel_leader_participation = on

# Logging
log_min_duration_statement = 1000  # Log slow queries > 1s
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on
log_temp_files = 1024
```

### Index Strategy

```sql
-- Composite indexes for query patterns
CREATE INDEX idx_orders_user_status_date 
    ON orders (user_id, status, created_at DESC);

-- Partial indexes for common filters
CREATE INDEX idx_orders_active 
    ON orders (user_id, created_at DESC) 
    WHERE status = 'active';

-- Covering indexes for index-only scans
CREATE INDEX idx_orders_covering 
    ON orders (user_id, status) 
    INCLUDE (total_amount, created_at);
```

## Backup Validation

### Automated Restore Testing

```bash
#!/bin/bash
# Weekly restore test
./scripts/test_restore.sh \
  --source=latest \
  --target=restore-test \
  --validate-schema \
  --validate-row-counts \
  --validate-checksums
```

### Validation Checklist

- [ ] Schema matches production
- [ ] Row counts match (±1% for active tables)
- [ ] Checksums match for critical tables
- [ ] Indexes rebuilt successfully
- [ ] Constraints and foreign keys valid
- [ ] Sequences at correct values
- [ ] Performance within 10% of production

## Compliance & Auditing

### Audit Logging

```sql
-- Enable pgaudit
CREATE EXTENSION pgaudit;

-- Configuration
pgaudit.log = 'all, -misc'
pgaudit.log_level = notice
pgaudit.log_parameter = on
pgaudit.log_relation = on
```

### Compliance Reports

```bash
# Generate compliance report
./scripts/compliance_report.sh \
  --standard=SOC2 \
  --period=monthly \
  --output=compliance-2024-01.pdf
```

## Troubleshooting

### Common Issues

| Issue | Diagnosis | Resolution |
|-------|-----------|------------|
| Replication lag > 1GB | Network, disk I/O, long transactions | Check `pg_stat_replication`, check `pg_stat_activity` for long queries |
| Primary fails | Hardware, network, OOM | Patroni automatic failover, check `patronictl list` |
| Backup fails | S3 permissions, disk space | Check pgBackRest logs, verify S3 credentials |
| Connection refused | max_connections, pg_hba.conf | Increase `max_connections`, check pg_hba.conf |
| High CPU | Missing indexes, bad queries | Check `pg_stat_statements`, add indexes |

### Diagnostic Queries

```sql
-- Active queries
SELECT pid, now() - query_start AS duration, state, query
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY duration DESC;

-- Table sizes
SELECT schemaname, tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Index usage
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;

-- Cache hit ratio
SELECT sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) as hit_ratio
FROM pg_statio_user_tables;
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-01-15 | Initial enterprise release |
| 1.1.0 | 2024-01-20 | Added HA and monitoring |
| 1.2.0 | 2024-01-25 | Added backup and PITR |
| 2.0.0 | 2024-07-09 | Enterprise rewrite for Hackathon III |

## Related Documentation

- [Patroni Documentation](https://patroni.readthedocs.io/)
- [pgBackRest Documentation](https://pgbackrest.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Kubernetes Operator for PostgreSQL](https://github.com/zalando/postgres-operator)