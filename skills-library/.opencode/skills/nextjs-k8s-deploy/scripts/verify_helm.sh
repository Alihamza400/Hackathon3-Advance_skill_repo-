#!/bin/bash
# Verify Next.js application deployment in Kubernetes

APP_NAME="$1"
NAMESPACE="default"
TIMEOUT_SECONDS=300 # 5 minutes timeout for readiness

if [ -z "$APP_NAME" ]; then
    echo "Usage: $0 <app-name> [--namespace <namespace>]"
    echo "Example: $0 learnflow-frontend --namespace production"
    exit 1
}

while [[ $# -gt 0 ]]; do
    case $1 in
        --namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

# Load deployment info (if available)
if [ -f "../.nextjs-deployment-info" ]; then
    source ../.nextjs-deployment-info
    # Override with command line arguments if provided
    APP_NAME=${1:-$APP_NAME}
    NAMESPACE=${2:-$NAMESPACE}
fi

echo "Verifying Next.js application '$APP_NAME' deployment in namespace '$NAMESPACE'..."

# 1. Check Helm Release Status
echo "\n=== Step 1: Checking Helm Release Status ==="
HELM_STATUS=$(helm status "$APP_NAME" -n "$NAMESPACE" 2>/dev/null | grep "Status" | awk '{print $2}')
if [ "$HELM_STATUS" == "deployed" ]; then
    echo "✓ Helm release '$APP_NAME' is deployed."
else
    echo "❌ Helm release '$APP_NAME' is not deployed or in a failed state (Status: $HELM_STATUS)."
    exit 1
}

# 2. Check Deployment Readiness
echo "\n=== Step 2: Checking Deployment Readiness ==="
if kubectl wait --for=condition=Available --timeout=${TIMEOUT_SECONDS}s deployment/"$APP_NAME" -n "$NAMESPACE" >/dev/null 2>&1; then
    echo "✓ Deployment '$APP_NAME' is Available."
else
    echo "❌ Deployment '$APP_NAME' did not become Available within ${TIMEOUT_SECONDS}s."
    exit 1
}

# 3. Check Pods Status
echo "\n=== Step 3: Checking Pods Status ==="
PODS_READY=$(kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/instance="$APP_NAME" -o jsonpath='{.items[*].status.containerStatuses[*].ready}' 2>/dev/null | grep -o true | wc -l)
EXPECTED_REPLICAS=$(kubectl get deployment "$APP_NAME" -n "$NAMESPACE" -o jsonpath='{.spec.replicas}' 2>/dev/null)

if [ -z "$EXPECTED_REPLICAS" ]; then
    echo "❌ Could not determine expected replicas for deployment '$APP_NAME'."
    exit 1
}

if [ "$PODS_READY" -ge "$EXPECTED_REPLICAS" ]; then
    echo "✓ All ($PODS_READY/$EXPECTED_REPLICAS) Next.js pods are Running and Ready."
else
    echo "❌ Only ($PODS_READY/$EXPECTED_REPLICAS) Next.js pods are Running and Ready. Please investigate."
    kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/instance="$APP_NAME" # Show pod status for debugging
    exit 1
}

# 4. Check Service Endpoints
echo "\n=== Step 4: Checking Service Endpoints ==="
SERVICE_NAME_K8S=$(kubectl get service -n "$NAMESPACE" -l app.kubernetes.io/instance="$APP_NAME" -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
SERVICE_IP=$(kubectl get service "$SERVICE_NAME_K8S" -n "$NAMESPACE" -o jsonpath='{.spec.clusterIP}' 2>/dev/null)

if [ -z "$SERVICE_IP" ]; then
    echo "❌ Service for '$APP_NAME' not found or has no ClusterIP."
    exit 1
}

echo "✓ Service '$SERVICE_NAME_K8S' has ClusterIP: $SERVICE_IP."

# 5. Check Ingress (if enabled)
echo "\n=== Step 5: Checking Ingress ==="
INGRESS_HOST=$(kubectl get ingress "$APP_NAME" -n "$NAMESPACE" -o jsonpath='{.spec.rules[0].host}' 2>/dev/null)
if [ ! -z "$INGRESS_HOST" ]; then
    echo "✓ Ingress found for '$APP_NAME' at host: $INGRESS_HOST."
    # Attempt to curl the ingress host (requires external access to cluster or /etc/hosts entry)
    echo "Attempting to reach Ingress host (may require external access or local DNS resolution)..."
    if curl -s --head "http://$INGRESS_HOST" | grep -q "200 OK"; then
        echo "✓ Ingress host '$INGRESS_HOST' is reachable (200 OK)."
    else
        echo "⚠️ Warning: Ingress host '$INGRESS_HOST' not directly reachable or returned non-200 status. Manual check needed."
    fi
else
    echo "ℹ Ingress not found or not configured for '$APP_NAME'."
}

# Final validation
echo "\n=== Final Validation ==="
echo "🎉 Next.js application '$APP_NAME' deployment verification complete!"

# Only this output enters agent context:
echo "✓ Next.js app '$APP_NAME' deployment verified successfully."
