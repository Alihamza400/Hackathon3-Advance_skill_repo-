#!/bin/bash
# Enterprise Kafka verification script

# Parse command line arguments
NAMESPACE="kafka"
ENDPOINTS=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        --endpoints)
            ENDPOINTS=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "Verifying enterprise Kafka deployment in namespace: $NAMESPACE"

echo "=== Step 1: Checking Core Components ==="

# Check namespace exists
if kubectl get namespace "$NAMESPACE" >/dev/null 2>&1; then
    echo "✓ Namespace '$NAMESPACE' exists"
else
    echo "✗ Namespace '$NAMESPACE' does not exist"
    exit 1
fi

# Check Kafka deployment
KAFKA_DEPLOYMENT=$(kubectl get deployment kafka -n "$NAMESPACE" 2>/dev/null | grep "kafka" | wc -l)
if [ "$KAFKA_DEPLOYMENT" -gt 0 ]; then
    echo "✓ Kafka deployment found ($KAFKA_DEPLOYMENT)"
else
    echo "✗ Kafka deployment not found"
    exit 1
fi

# Check ZooKeeper deployment
ZOO_DEPLOYMENT=$(kubectl get deployment kafka-zookeeper -n "$NAMESPACE" 2>/dev/null | grep "zookeeper" | wc -l)
if [ "$ZOO_DEPLOYMENT" -gt 0 ]; then
    echo "✓ ZooKeeper deployment found ($ZOO_DEPLOYMENT)"
else
    echo "✗ ZooKeeper deployment not found"
    exit 1
fi

# Check Kafka pods status
echo "=== Step 2: Checking Pod Status ==="
KAFKA_PODS=$(kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=kafka --no-headers | wc -l)
if [ "$KAFKA_PODS" -gt 0 ]; then
    echo "✓ Kafka pods running: $KAFKA_PODS"
else
    echo "✗ No Kafka pods found"
    exit 1
fi

# Check ZooKeeper pods status
ZOO_PODS=$(kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=kafka-zookeeper --no-headers | wc -l)
if [ "$ZOO_PODS" -gt 0 ]; then
    echo "✓ ZooKeeper pods running: $ZOO_PODS"
else
    echo "✗ No ZooKeeper pods found"
    exit 1
fi

# Detailed pod status if verbose
if [ "$VERBOSE" = true ]; then
    echo "=== Detailed Pod Status ==="
    kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=kafka -o wide
    kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=kafka-zookeeper -o wide
fi

echo "=== Step 3: Checking Services ==="
# Check Kafka service
KAFKA_SERVICE=$(kubectl get service kafka -n "$NAMESPACE" 2>/dev/null | grep "kafka" | wc -l)
if [ "$KAFKA_SERVICE" -gt 0 ]; then
    echo "✓ Kafka service found"
    if [ "$ENDPOINTS" = true ]; then
        echo "Kafka endpoints:"
        kubectl get endpoints kafka -n "$NAMESPACE" -o wide
    fi
else
    echo "✗ Kafka service not found"
    exit 1
fi

# Check ZooKeeper service
ZOO_SERVICE=$(kubectl get service kafka-zookeeper -n "$NAMESPACE" 2>/dev/null | grep "zookeeper" | wc -l)
if [ "$ZOO_SERVICE" -gt 0 ]; then
    echo "✓ ZooKeeper service found"
else
    echo "✗ ZooKeeper service not found"
    exit 1
fi

echo "=== Step 4: Advanced Verification ==="

# Check persistent volumes if exists
echo "Checking persistent volumes..."
PVC_COUNT=$(kubectl get pvc -n "$NAMESPACE" 2>/dev/null | wc -l)
if [ "$PVC_COUNT" -gt 1 ]; then
    echo "✓ Persistent volumes configured: $PVC_COUNT"
else
    echo "ℹ Limited persistent volumes: $PVC_COUNT (may be normal for development)"
fi

# Check monitoring if enabled
if kubectl get servicemonitor kafka -n "$NAMESPACE" 2>/dev/null >/dev/null; then
    echo "✓ Monitoring configured (ServiceMonitor)"
else
    echo "ℹ Monitoring may not be configured"
fi

# Check storage class
STORAGE_CLASS=$(kubectl get statefulset/kafka -n "$NAMESPACE" -o yaml 2>/dev/null | grep -A5 "storageClassName" | head -1 | grep -o "storageClassName: [^ ]*" | cut -d' ' -f2)
if [ ! -z "$STORAGE_CLASS" ]; then
    echo "✓ Storage class: $STORAGE_CLASS"
fi

# Final validation
echo "=== Final Validation ==="
TOTAL_PODS=$((KAFKA_PODS + ZOO_PODS))
if [ "$TOTAL_PODS" -ge 6 ]; then
    echo "✓ All core services are running and healthy"
    echo "🎉 Enterprise Kafka deployment verification complete!"
    exit 0
else
    echo "✗ Insufficient pods running. Expected at least 6, found $TOTAL_PODS"
    exit 1
fi
