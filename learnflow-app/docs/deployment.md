# Deployment

## Local Development

Run each microservice individually with hot-reload:

```bash
cd services/<service-name>
uvicorn main:app --reload --port <port>
```

For the frontend:

```bash
cd frontend
npm run dev
```

## Docker

Each service has a Dockerfile. Build and run with Docker Compose:

```bash
# Build all services
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

## Kubernetes

Kubernetes manifests are located in `k8s/`. Deploy with:

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/redis/
kubectl apply -f k8s/postgres/
kubectl apply -f k8s/services/
kubectl apply -f k8s/gateway/
```

## Production Considerations

- **Scaling**: Each microservice scales independently based on load. The Triage and Concepts agents typically see the most traffic.
- **Caching**: Redis is used for response caching (concept explanations, code reviews) and session management.
- **Rate Limiting**: Gateway enforces per-endpoint rate limits (100 req/min default, 20 req/min for auth).
- **Security**: JWT-based auth with token blacklisting. Sandboxed code execution with resource limits (5s CPU, 50MB memory).
- **Monitoring**: Health check endpoints at `/health`, `/healthz`, `/ready` for Kubernetes liveness/readiness probes.
- **Dapr**: Use Dapr for resilient service-to-service communication with retries, timeouts, and observability.
