# FastAPI Dapr Agent Skill - Enterprise Reference

## Overview
The `fastapi-dapr-agent` skill provides enterprise-grade scaffolding for building microservices using FastAPI with Dapr (Distributed Application Runtime) sidecars. It implements industry best practices for distributed systems including state management, pub/sub messaging, service invocation, and observability.

## Skill Architecture

### File Structure
```
fastapi-dapr-agent/
├── SKILL.md                 # Agent instructions (~100 tokens)
├── REFERENCE.md             # This document (loaded on-demand)
└── scripts/
    ├── create_service.sh   # Scaffold FastAPI + Dapr microservice
    ├── configure_dapr.sh   # Apply Dapr component manifests
    ├── deploy_service.sh   # Deploy to Kubernetes with Dapr
    ├── verify.py           # Comprehensive service verification
    └── test_service.sh     # Functional API testing
```

## Enterprise Features

### 1. Microservice Scaffolding
The `create_service.sh` script generates a production-ready FastAPI service with:

- **FastAPI Application Structure**: Modular routes, dependency injection, Pydantic models
- **Dapr Integration**: State management, pub/sub, service invocation, secrets
- **OpenAPI Documentation**: Auto-generated Swagger/OpenAPI specs
- **Health Checks**: Liveness/readiness probes for Kubernetes
- **Structured Logging**: JSON logging with correlation IDs
- **Error Handling**: Standardized error responses with trace IDs
- **Security**: Input validation, rate limiting headers, CORS configuration

### 2. Dapr Component Configuration
The `configure_dapr.sh` script manages:

- **State Store**: Redis-backed state management with transactions
- **Pub/Sub**: Redis Streams for event-driven communication
- **Service Invocation**: mTLS-secured service-to-service calls
- **Secret Store**: Kubernetes secrets integration
- **Configuration**: Distributed configuration management
- **Bindings**: Input/output bindings for external systems

### 3. Kubernetes Deployment
The `deploy_service.sh` script handles:

- **Container Image**: Multi-stage Docker build (build + runtime)
- **Dapr Annotations**: Sidecar injection, app ID, port configuration
- **Resource Management**: CPU/memory requests/limits, QoS classes
- **Security Context**: Non-root user, read-only filesystem, dropped capabilities
- **Horizontal Pod Autoscaler**: CPU/memory-based scaling
- **Pod Disruption Budget**: High availability during maintenance

### 4. Comprehensive Verification
The `verify.py` script validates:

- Deployment readiness and availability
- Pod health (main container + Dapr sidecar)
- Dapr component registration and health
- Service endpoints and DNS resolution
- Pub/Sub subscription endpoints
- Health endpoint responsiveness

### 4. Functional Testing
The `test_service.sh` script executes:

- REST API endpoint testing (health, root, CRUD operations)
- Dapr state management (save/get state)
- Dapr pub/sub (publish events)
- Service invocation (inter-service calls)
- Error handling and validation

## Architecture Patterns

### Service Structure
```
services/{service-name}/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── Dockerfile             # Multi-stage container build
├── k8s/
│   ├── deployment.yaml    # Kubernetes deployment + Dapr annotations
│   ├── service.yaml       # ClusterIP service
│   ├── hpa.yaml           # Horizontal pod autoscaler
│   └── pdb.yaml           # Pod disruption budget
├── dapr/
│   ├── components/        # Dapr component manifests
│   │   ├── statestore.yaml
│   │   ├── pubsub.yaml
│   │   └── secretstore.yaml
│   └── appconfig.yaml     # Dapr configuration
└── tests/
    ├── test_api.py        # API endpoint tests
    ├── test_dapr.py       # Dapr integration tests
    └── test_contract.py   # Contract tests
```

### Dapr Integration Patterns

#### State Management
```python
# Save state
await dapr_client.save_state(
    store_name="statestore",
    key="user:123",
    value={"name": "John", "preferences": {"theme": "dark"}}
)

# Get state
state = await dapr_client.get_state(
    store_name="statestore",
    key="user:123"
)
```

#### Pub/Sub Messaging
```python
# Publish event
await dapr_client.publish_event(
    pubsub_name="pubsub",
    topic_name="user.events",
    data={"user_id": "123", "action": "created"},
    data_content_type="application/json"
)

# Subscribe (in main.py)
@app.post("/events/user.created")
async def handle_user_created(event: CloudEvent):
    # Process user creation event
    pass
```

#### Service Invocation
```python
# Call another service
response = await dapr_client.invoke_method(
    app_id="payment-service",
    method_name="process",
    data={"order_id": "123", "amount": 99.99}
)
```

## Dapr Component Specifications

### State Store (Redis)
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.redis
  version: v1
  metadata:
  - name: redisHost
    value: "redis-master.default.svc.cluster.local:6379"
  - name: redisPassword
    secretKeyRef:
      name: redis
      key: redis-password
  - name: enableTLS
    value: "true"
```

### Pub/Sub (Redis Streams)
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
spec:
  type: pubsub.redis
  version: v1
  metadata:
  - name: redisHost
    value: "redis-master.default.svc.cluster.local:6379"
  - name: redisPassword
    secretKeyRef:
      name: redis
      key: redis-password
  - name: enableTLS
    value: "true"
```

### Secret Store (Kubernetes)
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: secretstore
spec:
  type: secretstores.kubernetes
  version: v1
```

## Enterprise Security

### Network Security
```yaml
# NetworkPolicy for service isolation
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: {service-name}-policy
spec:
  podSelector:
    matchLabels:
      app: {service-name}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: dapr-system
    - podSelector:
        matchLabels:
          app: dapr-sidecar
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: TCP
      port: 53
```

### Security Context
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  runAsGroup: 1000
  fsGroup: 1000
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
  capabilities:
    drop: ["ALL"]
```

### mTLS Configuration
```yaml
# Dapr Configuration for mTLS
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: appconfig
spec:
  mtls:
    enabled: true
    workloadCertTTL: "24h"
    allowedClockSkew: "15m"
```

## Observability Stack

### Distributed Tracing
```yaml
# Dapr tracing configuration
tracing:
  samplingRate: "1"
  zipkin:
    endpointAddress: "http://zipkin.observability.svc.cluster.local:9411/api/v1/spans"
```

### Metrics
```yaml
# Prometheus metrics
metric:
  enabled: true
  prometheus:
    port: 9090
    path: "/metrics"
```

### Structured Logging
```python
import structlog

logger = structlog.get_logger()

# Add correlation ID to all logs
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
```

## Performance Optimization

### Connection Pooling
```python
# Redis connection pool
redis_pool = redis.ConnectionPool(
    host="redis-master",
    port=6379,
    max_connections=20,
    retry_on_timeout=True
)

# HTTP client pooling
async with httpx.AsyncClient(
    limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
    timeout=30.0
) as client:
    pass
```

### Caching Strategy
```python
# Cache-aside pattern with TTL
async def get_user(user_id: str):
    # Try cache first
    cached = await dapr_client.get_state("statestore", f"user:{user_id}")
    if cached:
        return cached
    
    # Fetch from database
    user = await db.get_user(user_id)
    
    # Cache with TTL
    await dapr_client.save_state("statestore", f"user:{user_id}", user)
    return user
```

## Testing Strategy

### Unit Tests
```python
# test_api.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_state_management():
    # Test Dapr state operations
    response = client.post("/state/test-key", json={"value": "test"})
    assert response.status_code == 200
    
    get_response = client.get("/state/test-key")
    assert get_response.json()["value"] == "test"
```

### Contract Testing
```python
# test_contract.py
from pact import Consumer, Provider

pact = Consumer("frontend").has_pact_with(Provider("user-service"))

def test_get_user_contract():
    (pact
     .given("User 123 exists")
     .upon_receiving("a request for user 123")
     .with_request("GET", "/users/123")
     .will_respond_with(200, body={"id": "123", "name": "John"}))
     
    with pact:
        response = requests.get(f"{base_url}/users/123")
        assert response.status_code == 200
```

### Load Testing
```bash
# k6 load test
k6 run --vus 100 --duration 30s load-test.js
```

## Deployment Strategies

### Blue-Green Deployment
```yaml
# Deploy new version to green namespace
kubectl apply -f k8s/green/
# Switch traffic
kubectl patch service my-service -p '{"spec":{"selector":{"version":"green"}}}'
# Rollback if needed
kubectl patch service my-service -p '{"spec":{"selector":{"version":"blue"}}}'
```

### Canary Deployment
```yaml
# Flagger canary analysis
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: my-service
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-service
  service:
    port: 8000
  analysis:
    interval: 1m
    threshold: 5
    metrics:
    - name: request-success-rate
      threshold: 99
      interval: 1m
```

## Troubleshooting

### Common Issues

| Issue | Diagnosis | Resolution |
|-------|-----------|------------|
| Dapr sidecar not starting | Check sidecar logs | `kubectl logs -l app=myservice -c daprd` |
| State store not accessible | Check Redis connectivity | `kubectl exec -it pod -- redis-cli ping` |
| Pub/Sub not delivering | Check subscription endpoint | Verify `/dapr/subscribe` endpoint returns routes |
| Service invocation fails | Check mTLS, service name | Verify Dapr app-id matches service name |
| High latency | Check Dapr metrics | Check `dapr.io/metrics` endpoint |

### Diagnostic Commands
```bash
# Check Dapr sidecar status
kubectl get pods -l app=myservice -o wide

# Check Dapr components
kubectl get components

# Check Dapr subscriptions
kubectl get subscriptions

# View Dapr logs
kubectl logs -l app=myservice -c daprd --tail=100

# Check Dapr configuration
kubectl get configuration appconfig -o yaml

# Test service invocation
dapr invoke --app-id payment-service --method process -d '{"amount": 100}'
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-01-15 | Initial enterprise release |
| 1.1.0 | 2024-01-20 | Added Dapr components |
| 1.2.0 | 2024-01-25 | Added security hardening |
| 2.0.0 | 2024-07-09 | Enterprise rewrite for Hackathon III |

## Related Documentation

- [Dapr Documentation](https://docs.dapr.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Dapr Python SDK](https://github.com/dapr/python-sdk)
- [Kubernetes Dapr Integration](https://docs.dapr.io/operations/hosting/kubernetes/kubernetes-overview/)