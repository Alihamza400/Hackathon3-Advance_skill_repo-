# Architecture

## System Architecture Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                         Client Apps                          │
│            (Web App / CLI / API Consumers)                    │
└──────────────────────────┬───────────────────────────────────┘
                           │ HTTPS
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                    API Gateway (:8000)                        │
│         Auth, Rate Limiting, Request Routing, Logging         │
└──────┬──────┬──────┬──────┬──────┬──────┬──────┬────────────┘
       │      │      │      │      │      │      │
       ▼      ▼      ▼      ▼      ▼      ▼      ▼
┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
│ Auth │ │Triage│ │Conc.│ │Code │ │Debug │ │Exerc.│ │Prog. │
│:8001 │ │:8002 │ │:8003 │ │Rev  │ │:8005 │ │:8006 │ │:8007 │
│      │ │      │ │      │ │:8004 │ │      │ │      │ │      │
└──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘
   │        │        │        │        │        │        │
   └────────┴────────┴────────┴────────┴────────┴────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │   Shared Infrastructure │
              │  (Redis, Postgres,      │
              │   Kafka, Dapr Sidecar)  │
              └────────────────────────┘
```

## Microservices Overview

| Service | Port | Responsibility |
|---------|------|---------------|
| API Gateway | 8000 | Central routing, auth, rate limiting, CORS |
| Auth Service | 8001 | User registration, login, JWT management, RBAC |
| Triage Agent | 8002 | Query classification and routing to specialist agents |
| Concepts Agent | 8003 | Python concept explanations at multiple difficulty levels |
| Code Review Agent | 8004 | Static analysis, style checks, security audits, metrics |
| Debug Agent | 8005 | Error analysis, sandboxed code execution, fix suggestions |
| Exercise Agent | 8006 | Exercise generation, test case execution, grading |
| Progress Agent | 8007 | Mastery tracking, streaks, dashboards, struggle detection |

## Data Flow

1. **Client Request** → API Gateway validates auth, applies rate limits
2. **Triage** → Gateway forwards queries to Triage Agent for classification
3. **Routing** → Triage routes to the appropriate specialist agent
4. **Processing** → Specialist agent processes the request using its knowledge base
5. **Events** → Agents publish events to Kafka for analytics and progress tracking
6. **Response** → Results flow back through the gateway to the client

## Deployment Architecture

- **Containerized**: Each service runs in its own Docker container
- **Orchestration**: Kubernetes for production deployments
- **Service Mesh**: Dapr sidecars handle service-to-service communication
- **Database**: PostgreSQL for persistent storage, Redis for caching and sessions
- **Messaging**: Kafka for event-driven communication between agents
- **Frontend**: Next.js static site served via CDN or Nginx
