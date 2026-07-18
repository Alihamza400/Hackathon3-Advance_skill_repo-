#!/bin/bash
set -e

SERVICES_DIR="$(cd "$(dirname "$0")/services" && pwd)"
VENV_DIR="$(cd "$(dirname "$0")/../venv" && pwd)"
PYTHON="$VENV_DIR/bin/python"

echo "Starting LearnFlow services..."
echo "Services dir: $SERVICES_DIR"

declare -A PORTS
PORTS[auth]=8001
PORTS[triage]=8002
PORTS[concepts]=8003
PORTS[code-review]=8004
PORTS[debug]=8005
PORTS[exercise]=8006
PORTS[progress]=8007
PORTS[gateway]=8000

PIDS=()

cleanup() {
    echo ""
    for pid in "${PIDS[@]}"; do
        kill "$pid" 2>/dev/null || true
    done
    echo "All services stopped."
    exit 0
}

trap cleanup SIGINT SIGTERM

export PYTHONPATH="$SERVICES_DIR"

cd "$SERVICES_DIR"

for service in auth triage concepts code-review debug exercise progress; do
    echo "Starting $service-service on port ${PORTS[$service]}..."
    PORT="${PORTS[$service]}" "$PYTHON" "$service/main.py" &
    PIDS+=($!)
    sleep 1
done

echo "Starting gateway on port ${PORTS[gateway]}..."
PORT="${PORTS[gateway]}" "$PYTHON" gateway/main.py &
PIDS+=($!)
sleep 1

echo ""
echo "All services started."
echo "Gateway: http://localhost:${PORTS[gateway]}"
echo "Auth:    http://localhost:${PORTS[auth]}"
echo "Press Ctrl+C to stop all."
echo ""

wait
