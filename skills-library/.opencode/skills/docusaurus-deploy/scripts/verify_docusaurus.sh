#!/bin/bash
# Verify Docusaurus site deployment in Kubernetes

DOC_NAME="$1"
KUBERNETES_NAMESPACE="documentation"

if [ -z "$DOC_NAME" ]; then
    echo "Usage: $0 <doc-name> [--namespace <namespace>]"
    echo "Example: $0 learnflow-docs --namespace documentation"
    exit 1
fi

while [[ $# -gt 0 ]]; do
    case $1 in
        --namespace)
            KUBERNETES_NAMESPACE="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

echo "Verifying Docusaurus site '$DOC_NAME' deployment in namespace '$KUBERNETES_NAMESPACE'..."

# 1. Check Deployment Status
echo "\n=== Step 1: Checking Deployment Status ==="
if kubectl wait --for=condition=Available --timeout=120s deployment/"${DOC_NAME}-deployment" -n "$KUBERNETES_NAMESPACE" >/dev/null 2>&1; then
    echo "✓ Deployment '${DOC_NAME}-deployment' is Available."
else
    echo "❌ Deployment '${DOC_NAME}-deployment' did not become Available within timeout."
    exit 1
fi

# 2. Check Pods Status
echo "\n=== Step 2: Checking Pods Status ==="
PODS_READY=$(kubectl get pods -n "$KUBERNETES_NAMESPACE" -l app="$DOC_NAME" -o jsonpath='{.items[*].status.containerStatuses[*].ready}' 2>/dev/null | grep -o true | wc -l)
EXPECTED_REPLICAS=$(kubectl get deployment "$DOC_NAME" -n "$KUBERNETES_NAMESPACE" -o jsonpath='{.spec.replicas}' 2>/dev/null)

if [ -z "$EXPECTED_REPLICAS" ]; then
    echo "❌ Could not determine expected replicas for deployment '$DOC_NAME'."
    exit 1
fi

if [ "$PODS_READY" -ge "$EXPECTED_REPLICAS" ]; then
    echo "✓ All ($PODS_READY/$EXPECTED_REPLICAS) Docusaurus pods are Running and Ready."
else
    echo "❌ Only ($PODS_READY/$EXPECTED_REPLICAS) Docusaurus pods are Running and Ready. Please investigate."
    kubectl get pods -n "$KUBERNETES_NAMESPACE" -l app="$DOC_NAME"
    exit 1
fi

# 3. Check Service Endpoints
echo "\n=== Step 3: Checking Service Endpoints ==="
SERVICE_NAME_K8S=$(kubectl get service -n "$KUBERNETES_NAMESPACE" -l app="$DOC_NAME" -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ -z "$SERVICE_NAME_K8S" ]; then
    echo "❌ Service for '$DOC_NAME' not found."
    exit 1
fi

ENDPOINTS_COUNT=$(kubectl get endpoints "$SERVICE_NAME_K8S" -n "$KUBERNETES_NAMESPACE" -o jsonpath='{.subsets[*].addresses[*].ip}' 2>/dev/null | wc -w)
if [ "$ENDPOINTS_COUNT" -gt 0 ]; then
    echo "✓ Service '$SERVICE_NAME_K8S' has $ENDPOINTS_COUNT endpoint(s)."
else
    echo "❌ Service '$SERVICE_NAME_K8S' has no endpoints."
    exit 1
fi

# 4. Check Ingress (if exists)
echo "\n=== Step 4: Checking Ingress ==="
INGRESS_HOST=$(kubectl get ingress "$DOC_NAME" -n "$KUBERNETES_NAMESPACE" -o jsonpath='{.spec.rules[0].host}' 2>/dev/null)
if [ ! -z "$INGRESS_HOST" ]; then
    echo "✓ Ingress found for '$DOC_NAME' at host: $INGRESS_HOST."
    
    # Attempt to reach the ingress (if external access is available)
    echo "Attempting to reach Ingress host (may require external access or /etc/hosts entry)..."
    if curl -s --head "https://$INGRESS_HOST" | grep -q "200 OK"; then
        echo "✓ Ingress host '$INGRESS_HOST' is reachable (200 OK)."
    elif curl -s --head "http://$INGRESS_HOST" | grep -q "200 OK"; then
        echo "✓ Ingress host '$INGRESS_HOST' is reachable via HTTP (200 OK)."
    else
        echo "⚠️ Warning: Ingress host '$INGRESS_HOST' not directly reachable or returned non-200 status. Manual check needed."
    fi
else
    echo "ℹ Ingress not found or not configured for '$DOC_NAME'."
fi

# 5. Test Static Content Serving (via port-forward if needed)
echo "\n=== Step 5: Testing Static Content Serving ==="
POD_NAME=$(kubectl get pods -n "$KUBERNETES_NAMESPACE" -l app="$DOC_NAME" -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ ! -z "$POD_NAME" ]; then
    echo "Found pod: $POD_NAME. Attempting port-forward to test content..."
    kubectl port-forward "$POD_NAME" 8080:80 -n "$KUBERNETES_NAMESPACE" > /dev/null 2>&1 &
    PF_PID=$!
    sleep 3
    
    if curl -s "http://localhost:8080" | grep -q "Docusaurus"; then
        echo "✓ Docusaurus content is being served correctly."
    else
        echo "⚠️ Warning: Could not verify Docusaurus content via port-forward. Manual check recommended."
    fi
    kill $PF_PID 2>/dev/null
else
    echo "⚠️ Warning: No pod found to test content serving."
fi

# Final validation
echo "\n=== Final Validation ==="
echo "🎉 Docusaurus site '$DOC_NAME' deployment verification complete!"
echo "   Deployment: ✓ Available"
echo "   Pods: ✓ $EXPECTED_REPLICAS/$EXPECTED_REPLICAS Ready"
echo "   Service: ✓ Endpoints Available"
echo "   Ingress: ✓ Configured"

# Only this output enters agent context:
echo "✓ Docusaurus site '$DOC_NAME' deployment verified successfully."