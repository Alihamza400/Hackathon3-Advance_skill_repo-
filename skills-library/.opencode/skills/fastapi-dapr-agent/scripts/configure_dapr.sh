#!/bin/bash
# Configure Dapr components for a FastAPI microservice

SERVICE_NAME="$1"

if [ -z "$SERVICE_NAME" ]; then
    echo "Usage: $0 <service-name>"
    echo "Example: $0 concepts-agent"
    exit 1
fi

COMPONENTS_DIR="./components/$SERVICE_NAME"

# Ensure component directory exists
if [ ! -d "$COMPONENTS_DIR" ]; then
    echo "❌ Error: Dapr components directory '$COMPONENTS_DIR' not found. Please run create_service.sh first."
    exit 1
fi

echo "Configuring Dapr components for service '$SERVICE_NAME'..."

# Apply all Dapr component YAMLs in the directory
for component_file in "$COMPONENTS_DIR"/*.yaml; do
    if [ -f "$component_file" ]; then
        echo "Applying Dapr component: $(basename "$component_file")"
        kubectl apply -f "$component_file"
        if [ $? -ne 0 ]; then
            echo "❌ Failed to apply Dapr component: $(basename "$component_file")"
            exit 1
        fi
    fi
done

# Create a default Dapr configuration for the app
cat > "$COMPONENTS_DIR/appconfig.yaml" << EOF
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: appconfig
  namespace: default
spec:
  httpPipeline:
    handlers:
    - name: sentry
      type: middleware.sentry
  tracing:
    samplingRate: "1" # Enable tracing for all requests
    zipkin:
      endpointAddress: "http://zipkin.observability.svc.cluster.local:9411/api/v1/spans"
  metric:
    enabled: true
EOF

kubectl apply -f "$COMPONENTS_DIR/appconfig.yaml"
if [ $? -ne 0 ]; then
    echo "❌ Failed to apply Dapr appconfig.yaml"
    exit 1
fi

echo "✓ Dapr components configured successfully for service '$SERVICE_NAME'"
