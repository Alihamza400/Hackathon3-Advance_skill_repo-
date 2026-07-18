#!/bin/bash
# Test FastAPI + Dapr microservice functionality

SERVICE_NAME="$1"
KUBERNETES_NAMESPACE="default"
SERVICE_PORT="8000"
LOCAL_PORT="8080"

if [ -z "$SERVICE_NAME" ]; then
    echo "Usage: $0 <service-name>"
    echo "Example: $0 concepts-agent"
    exit 1
fi

echo "Testing FastAPI + Dapr service '$SERVICE_NAME'..."

# Find a running pod for port-forwarding
POD_NAME=$(kubectl get pods -n "$KUBERNETES_NAMESPACE" -l "app=$SERVICE_NAME" -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

if [ -z "$POD_NAME" ]; then
    echo "❌ Error: No running pods found for service '$SERVICE_NAME' in namespace '$KUBERNETES_NAMESPACE'."
    echo "   Please ensure the service is deployed and running using deploy_service.sh and verify.py."
    exit 1
fi

echo "Found pod: $POD_NAME. Attempting port-forward from $LOCAL_PORT to $SERVICE_PORT..."

# Start port-forwarding in the background
kubectl port-forward "$POD_NAME" "$LOCAL_PORT:$SERVICE_PORT" -n "$KUBERNETES_NAMESPACE" > /dev/null 2>&1 &
PF_PID=$!

# Ensure port-forward is established
sleep 5

if ! ps -p $PF_PID > /dev/null; then
    echo "❌ Error: Port-forwarding failed to start. Check if port $LOCAL_PORT is in use or if kubectl is working."
    exit 1
fi

echo "Port-forward established (PID: $PF_PID). Running tests..."

BASE_URL="http://localhost:$LOCAL_PORT"

# 1. Test Health Endpoint
echo "\n=== Test 1: Health Endpoint ==="
HEALTH_RESPONSE=$(curl -s "$BASE_URL/health")
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo "✓ Health check passed: $HEALTH_RESPONSE"
else
    echo "❌ Health check failed: $HEALTH_RESPONSE"
    kill $PF_PID
    exit 1
fi

# 2. Test Root Endpoint
echo "\n=== Test 2: Root Endpoint ==="
ROOT_RESPONSE=$(curl -s "$BASE_URL/")
if echo "$ROOT_RESPONSE" | grep -q "running"; then
    echo "✓ Root endpoint passed: $ROOT_RESPONSE"
else
    echo "❌ Root endpoint failed: $ROOT_RESPONSE"
    kill $PF_PID
    exit 1
fi

# 3. Test Dapr State Management (Save State)
TEST_KEY="user-settings-123"
TEST_VALUE='{ "theme": "dark", "notifications": true }'
echo "\n=== Test 3: Dapr Save State ==="
SAVE_STATE_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" -d "$TEST_VALUE" "$BASE_URL/save_state/$TEST_KEY")
if echo "$SAVE_STATE_RESPONSE" | grep -q "success"; then
    echo "✓ Dapr Save State passed: $SAVE_STATE_RESPONSE"
else
    echo "❌ Dapr Save State failed: $SAVE_STATE_RESPONSE"
    kill $PF_PID
    exit 1
fi

# 4. Test Dapr State Management (Get State)
echo "\n=== Test 4: Dapr Get State ==="
GET_STATE_RESPONSE=$(curl -s "$BASE_URL/get_state/$TEST_KEY")
if echo "$GET_STATE_RESPONSE" | grep -q "dark" && echo "$GET_STATE_RESPONSE" | grep -q "true"; then
    echo "✓ Dapr Get State passed: $GET_STATE_RESPONSE"
else
    echo "❌ Dapr Get State failed: $GET_STATE_RESPONSE"
    kill $PF_PID
    exit 1
fi

# 5. Test Dapr Pub/Sub (Publish Event - Note: Subscription endpoint is /dapr/subscribe for actual Dapr to call)
TEST_TOPIC="learning.events"
TEST_EVENT_DATA='{ "studentId": "s123", "lessonId": "l456", "action": "completed" }'
echo "\n=== Test 5: Dapr Publish Event ==="
PUBLISH_EVENT_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" -d "$TEST_EVENT_DATA" "$BASE_URL/publish_event/$TEST_TOPIC")
if echo "$PUBLISH_EVENT_RESPONSE" | grep -q "success"; then
    echo "✓ Dapr Publish Event passed: $PUBLISH_EVENT_RESPONSE"
else
    echo "❌ Dapr Publish Event failed: $PUBLISH_EVENT_RESPONSE"
    kill $PF_PID
    exit 1
fi


echo "\n🎉 All FastAPI + Dapr service tests completed successfully!"

# Clean up port-forwarding
kill $PF_PID

# Only this output enters agent context:
echo "✓ Service '$SERVICE_NAME' functionality verified."
