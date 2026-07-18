#!/bin/bash
# Configure Ingress for a Next.js application in Kubernetes

APP_NAME="$1"
NAMESPACE="default"
HOST_DOMAIN="your-enterprise.com" # Enterprise domain, replace with actual
INGRESS_CLASS="nginx" # Common enterprise ingress controller

if [ -z "$APP_NAME" ]; then
    echo "Usage: $0 <app-name> [--namespace <namespace>] [--host-domain <domain>] [--ingress-class <class>]"
    echo "Example: $0 learnflow-frontend --namespace production --host-domain mycorp.com"
    exit 1
}

while [[ $# -gt 0 ]]; do
    case $1 in
        --namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        --host-domain)
            HOST_DOMAIN="$2"
            shift 2
            ;;
        --ingress-class)
            INGRESS_CLASS="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

HELM_CHART_DIR="./helm-charts/$APP_NAME"

# Ensure Helm chart directory and ingress template exist
if [ ! -d "$HELM_CHART_DIR" ] || [ ! -f "$HELM_CHART_DIR/templates/ingress.yaml" ]; then
    echo "❌ Error: Helm chart or ingress template not found. Please run create_helm.sh first."
    exit 1
}

# Determine the hostname for the application
APP_HOSTNAME="${APP_NAME}.${HOST_DOMAIN}"

echo "Setting up Ingress for Next.js application '$APP_NAME' (Host: $APP_HOSTNAME) in namespace '$NAMESPACE'..."

# Update Helm values for ingress configuration
# This assumes the Helm chart's values.yaml has a structure for ingress.hosts
# We'll use `helm upgrade` to apply these changes dynamically.

# Create a temporary values file for ingress configuration
TEMP_VALUES_FILE="/tmp/${APP_NAME}-ingress-values.yaml"
cat > "$TEMP_VALUES_FILE" << EOF
ingress:
  enabled: true
  className: "${INGRESS_CLASS}"
  hosts:
    - host: "${APP_HOSTNAME}"
      paths:
        - path: /
          pathType: ImplementationSpecific
  tls:
    - secretName: ${APP_NAME}-tls-secret
      hosts:
        - "${APP_HOSTNAME}"
EOF

# Deploy/Upgrade Helm chart with ingress values
helm upgrade --install "$APP_NAME" "$HELM_CHART_DIR" --namespace "$NAMESPACE" -f "$TEMP_VALUES_FILE" --atomic --timeout 5m

if [ $? -ne 0 ]; then
    echo "❌ Failed to configure Ingress for '$APP_NAME'."
    rm -f "$TEMP_VALUES_FILE"
    exit 1
}

rm -f "$TEMP_VALUES_FILE"

echo "✓ Ingress configured for Next.js application '$APP_NAME' at http://$APP_HOSTNAME."

# Only this output enters agent context:
echo "✓ Ingress for '$APP_NAME' configured to host $APP_HOSTNAME. Verify access."
