#!/bin/bash
set -e

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="$BASE_DIR/services"

echo "=== LearnFlow Startup ==="
echo ""

# Check prerequisites
if ! docker ps &>/dev/null; then
    echo "❌ Docker not running. Please start Docker first."
    exit 1
fi

# Start databases if not running
if ! docker ps --format '{{.Names}}' | grep -q learnflow-postgres; then
    echo "Starting PostgreSQL..."
    docker rm -f learnflow-postgres 2>/dev/null || true
    docker run -d --name learnflow-postgres \
        -e POSTGRES_USER=learnflow \
        -e POSTGRES_PASSWORD=learnflow \
        -e POSTGRES_DB=learnflow \
        -p 5432:5432 postgres:16-alpine > /dev/null
    sleep 3
    docker exec -i learnflow-postgres psql -U learnflow -d learnflow < "$BASE_DIR/infra/k8s/postgres-init.sql" 2>/dev/null || true
    echo "  ✅ PostgreSQL ready"
else
    echo "  ✅ PostgreSQL already running"
fi

if ! docker ps --format '{{.Names}}' | grep -q learnflow-redis; then
    echo "Starting Redis..."
    docker rm -f learnflow-redis 2>/dev/null || true
    docker run -d --name learnflow-redis -p 6379:6379 redis:7-alpine > /dev/null
    echo "  ✅ Redis ready"
else
    echo "  ✅ Redis already running"
fi

echo ""

# Start microservices
declare -A PORTS=( [auth]=8001 [triage]=8002 [concepts]=8003 [code-review]=8004 [debug]=8005 [exercise]=8006 [progress]=8007 [gateway]=8000 )

for svc in auth triage concepts code-review debug exercise progress gateway; do
    port=${PORTS[$svc]}
    nohup "$BASE_DIR/../venv/bin/python" "$BASE_DIR/services/$svc/main.py" > /tmp/$svc.log 2>&1 &
    echo "  ✅ $svc (port $port) PID $!"
    sleep 0.5
done

echo ""
echo "Waiting for all services to initialize..."
sleep 10

echo ""
echo "=== Health Check ==="
all_ok=0
for port in 8000 8001 8002 8003 8004 8005 8006 8007; do
    resp=$(curl -s --max-time 5 http://localhost:$port/health 2>&1 | head -c 60)
    if [ -n "$resp" ]; then
        echo "  ✅ Port $port: $resp"
        ((all_ok++))
    else
        echo "  ❌ Port $port: no response"
    fi
done

echo ""
echo "=== $all_ok/8 services running ==="
echo "Frontend: cd frontend && npm run dev"
echo "Gateway:  http://localhost:8000/docs"
echo "Postgres: localhost:5432 (learnflow/learnflow)"
echo "Redis:    localhost:6379"
