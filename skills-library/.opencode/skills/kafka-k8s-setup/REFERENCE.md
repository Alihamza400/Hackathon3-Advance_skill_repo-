# Kafka Kubernetes Setup Skill - Enterprise Reference

## Overview
The `kafka-k8s-setup` skill provides enterprise-grade Apache Kafka deployment on Kubernetes with production-ready configurations for high availability, security, monitoring, and disaster recovery.

## Skill Architecture

### File Structure
```
kafka-k8s-setup/
├── SKILL.md                 # Agent instructions (~100 tokens)
├── REFERENCE.md             # This document (loaded on-demand)
└── scripts/
    ├── deploy.sh           # Production Kafka deployment
    └── verify.sh           # Comprehensive verification
```

## Enterprise Features

### 1. Production-Grade Deployment
The `deploy.sh` script implements:
- **High Availability**: 3+ broker replicas with ZooKeeper ensemble
- **Persistent Storage**: Enterprise storage classes (gp3, io1) with encryption
- **Security**: TLS/SSL encryption, SASL authentication, RBAC policies
- **Monitoring**: Prometheus JMX exporter, ServiceMonitor integration
- **Networking**: LoadBalancer service, internal cluster DNS
- **Resource Management**: CPU/memory limits, QoS guarantees

### 2. Advanced Configuration Options
```bash
# Enterprise deployment
./scripts/deploy.sh \
  --environment=production \
  --monitoring=true \
  --security=true \
  --ha-enabled=true \
  --backup-enabled=true

# Development deployment
./scripts/deploy.sh \
  --environment=development \
  --monitoring=false \
  --security=false
```

### 3. Comprehensive Verification
The `verify.sh` script validates:
- All pods in Running/Ready state
- ZooKeeper ensemble quorum
- Kafka broker ISR (In-Sync Replicas)
- Service endpoints and DNS resolution
- Persistent volume binding
- Monitoring integration (ServiceMonitor)
- Security policies (NetworkPolicy, RBAC)
- SSL/TLS certificate validity

## Architecture Details

### Kafka Cluster Topology
```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                         │
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │   Kafka Broker 1 │  │   Kafka Broker 2 │                 │
│  │   (Port 9092)    │  │   (Port 9092)    │                 │
│  └────────┬─────────┘  └────────┬─────────┘                 │
│           │                    │                             │
│           └────────┬───────────┘                             │
│                    ▼                                         │
│  ┌──────────────────────────────────────────┐               │
│  │         ZooKeeper Ensemble (3)           │               │
│  │         (Ports 2181, 2888, 3888)         │               │
│  └──────────────────────────────────────────┘               │
│                    │                                         │
│           ┌────────┴────────┐                                │
│           ▼                 ▼                                │
│  ┌──────────────┐    ┌──────────────┐                       │
│  │  Persistent  │    │  Persistent  │                       │
│  │   Volumes (Kafka)     │    │  (ZooKeeper) │                       │
│  └──────────────┘    └──────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

### Resource Specifications

| Component | Replicas | CPU Request | Memory Request | Storage |
|-----------|----------|-------------|----------------|---------|
| Kafka Broker | 3 | 500m | 2Gi | 50Gi (gp3) |
| ZooKeeper | 3 | 250m | 1Gi | 10Gi (gp3) |

### Security Configuration

#### Network Policies
```yaml
# Ingress from monitoring namespace
- from:
  - namespaceSelector:
      matchLabels:
        name: monitoring
  ports:
  - protocol: TCP
    port: 7071  # JMX Exporter
```

#### TLS/SSL Configuration
- Inter-broker encryption enabled
- Client authentication via SASL/SCRAM
- Certificate auto-generation via cert-manager
- Certificate rotation via cert-manager

#### RBAC Roles
```yaml
# Kafka Admin Role
rules:
- apiGroups: ["kafka.strimzi.io"]
  resources: ["kafkas", "kafkatopics", "kafkausers"]
  verbs: ["get", "list", "create", "update", "delete"]
```

## Monitoring & Observability

### Prometheus Metrics
- **JMX Exporter** on port 7071
- **ServiceMonitor** for automatic discovery
- Key metrics: `kafka_server_brokertopicmetrics_messagesinpersec`, `kafka_server_requestmetrics_avg_latency_ms`

### Grafana Dashboards
- Kafka Overview (broker health, topic metrics)
- Consumer Lag Monitoring
- ZooKeeper Health
- Disk Usage & Network I/O

### Alerting Rules
```yaml
- alert: KafkaBrokerDown
  expr: kafka_server_brokerstate != 3
  for: 1m
  labels:
    severity: critical
  annotations:
    summary: "Kafka broker {{ $labels.kafka_broker_id }} is down"
```

## Disaster Recovery

### Backup Strategy
- **ZooKeeper**: Daily snapshots to S3/GCS
- **Kafka Topics**: MirrorMaker2 cross-cluster replication
- **Configuration**: GitOps with ArgoCD

### Recovery Procedures
```bash
# Restore ZooKeeper from snapshot
./scripts/restore_zookeeper.sh --snapshot-date=2024-01-15

# Failover to standby cluster
./scripts/failover.sh --target-cluster=dr-cluster
```

## Script Interfaces

### deploy.sh
```bash
./scripts/deploy.sh \
  --environment=production \
  --monitoring=true \
  --security=true \
  --ha-enabled=true \
  --backup-enabled=true
```

**Options:**
| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `--environment` | development, staging, production | development | Deployment environment |
| `--monitoring` | true, false | false | Enable Prometheus monitoring |
| `--security` | true, false | false | Enable TLS/SASL security |
| `--ha-enabled` | true, false | false | Enable High Availability (3+ replicas) |
| `--backup-enabled` | true, false | false | Enable backup configuration |

### verify.sh
```bash
./scripts/verify.sh \
  --namespace=kafka \
  --endpoints=true \
  --verbose=true
```

**Options:**
| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `--namespace` | string | kafka | Kubernetes namespace |
| `--endpoints` | true, false | false | Verify service endpoints |
| `--verbose` | true, false | false | Verbose output |
| `--security` | true, false | false | Verify security policies |

## Enterprise Compliance

### Standards Alignment
- **SOC 2 Type II**: Audit logging, access controls
- **HIPAA**: Encryption at rest/transit, audit trails
- **GDPR**: Data residency, right to erasure
- **PCI DSS**: Network segmentation, encryption

### Audit Requirements
- All deployment actions logged with timestamps
- Configuration changes tracked in GitOps repo
- Access to Kafka cluster audited via Kafka ACLs
- Backup/restore operations logged

## Integration Patterns

### With GitOps (ArgoCD)
```yaml
# argocd-application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: kafka-cluster
spec:
  source:
    repoURL: https://github.com/enterprise/kafka-gitops
    path: clusters/production/kafka
  destination:
    server: https://kubernetes.default.svc
    namespace: kafka
```

### With Service Mesh (Istio)
```yaml
# VirtualService for Kafka
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: kafka-vs
spec:
  hosts:
  - kafka.kafka.svc.cluster.local
  http:
  - route:
    - destination:
        host: kafka.kafka.svc.cluster.local
```

## Troubleshooting

### Common Issues

| Symptom | Cause | Resolution |
|---------|-------|------------|
| Pods stuck in Pending | Insufficient resources | Increase cluster capacity or reduce replicas |
| ZooKeeper not forming quorum | Network policies blocking | Check NetworkPolicy allowing 2181/2888/3888 |
| Brokers not joining ISR | Network/DNS issues | Verify headless service and pod DNS |
| High consumer lag | Under-provisioned brokers | Scale brokers, increase partitions |
| TLS handshake failures | Certificate mismatch | Verify cert-manager issuance |

### Diagnostic Commands
```bash
# Check broker logs
kubectl logs -n kafka kafka-0 -c kafka

# Check ZooKeeper logs
kubectl logs -n kafka kafka-zookeeper-0 -c zookeeper

# Check ISR status
kubectl exec -n kafka kafka-0 -- kafka-topics.sh --bootstrap-server localhost:9092 --describe

# Check consumer groups
kubectl exec -n kafka kafka-0 -- kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list
```

## Performance Tuning

### Broker Configuration
```properties
# Producer tuning
linger.ms=5
batch.size=65536
compression.type=snappy

# Consumer tuning
fetch.min.bytes=1
fetch.max.wait.ms=500
max.poll.records=500

# Broker tuning
num.network.threads=8
num.io.threads=16
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
```

### OS-Level Tuning
```bash
# /etc/sysctl.conf
vm.swappiness=1
vm.dirty_ratio=80
vm.dirty_background_ratio=5
net.core.somaxconn=1024
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-01-15 | Initial enterprise release |
| 1.1.0 | 2024-01-20 | Added HA and monitoring |
| 1.2.0 | 2024-01-25 | Added security and backup |
| 2.0.0 | 2024-07-09 | Enterprise rewrite for Hackathon III |

## Support
- **Documentation**: This REFERENCE.md
- **Issues**: GitHub Issues in skills-library repo
- **Standards**: AAIF Standards (https://aaif.io/)
- **Kafka Docs**: https://kafka.apache.org/documentation/