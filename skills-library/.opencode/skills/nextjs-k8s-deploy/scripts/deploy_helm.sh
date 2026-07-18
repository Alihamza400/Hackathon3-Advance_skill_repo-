#!/bin/bash
# Deploy Next.js application to Kubernetes using Helm

APP_NAME="$1"
NAMESPACE="default"

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

HELM_CHART_DIR="./helm-charts/$APP_NAME"

# Ensure Helm chart directory exists
if [ ! -d "$HELM_CHART_DIR" ]; then
    echo "❌ Error: Helm chart directory '$HELM_CHART_DIR' not found. Please run create_helm.sh first."
    exit 1
}

# Ensure namespace exists or create it
echo "Ensuring Kubernetes namespace '$NAMESPACE' exists..."
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
if [ $? -ne 0 ]; then
    echo "❌ Failed to ensure namespace '$NAMESPACE'."
    exit 1
}

echo "Deploying Next.js application '$APP_NAME' to Kubernetes in namespace '$NAMESPACE' using Helm..."

# Deploy or upgrade the Helm chart
helm upgrade --install "$APP_NAME" "$HELM_CHART_DIR" --namespace "$NAMESPACE" \
    --atomic --timeout 5m # Atomic ensures full rollback on failure

if [ $? -ne 0 ]; then
    echo "❌ Failed to deploy/upgrade Helm chart for '$APP_NAME'."
    exit 1
}

echo "✓ Next.js application '$APP_NAME' deployment initiated. Use verify_helm.sh to check status."

# Store deployment info for verification script
echo "APP_NAME=$APP_NAME" > ../.nextjs-deployment-info
echo "NAMESPACE=$NAMESPACE" >> ../.nextjs-deployment-info

# Only this output enters agent context:
echo "✓ Next.js application '$APP_NAME' deployed to Kubernetes."
