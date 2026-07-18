#!/bin/bash
# Deploy FastAPI + Dapr microservice to Kubernetes

SERVICE_NAME="$1"
IMAGE_REGISTRY="your-docker-registry.io" # Replace with your actual registry
IMAGE_TAG="latest"
KUBERNETES_NAMESPACE="default"

if [ -z "$SERVICE_NAME" ]; then
    echo "Usage: $0 <service-name>"
    echo "Example: $0 concepts-agent"
    exit 1
fi

SERVICE_DIR="./services/$SERVICE_NAME"
K8S_MANIFESTS_DIR="./k8s-manifests/$SERVICE_NAME"

# Ensure service directory and manifests exist
if [ ! -d "$SERVICE_DIR" ]; then
    echo "❌ Error: Service directory '$SERVICE_DIR' not found. Please run create_service.sh first."
    exit 1
fi

if [ ! -d "$K8S_MANIFESTS_DIR" ]; then
    echo "❌ Error: Kubernetes manifests directory '$K8S_MANIFESTS_DIR' not found. Please run create_service.sh first."
    exit 1
fi

echo "Deploying FastAPI + Dapr service '$SERVICE_NAME'..."

# 1. Build Docker Image
echo "Building Docker image for '$SERVICE_NAME'..."
docker build -t "$SERVICE_NAME:$IMAGE_TAG" "$SERVICE_DIR"
if [ $? -ne 0 ]; then
    echo "❌ Failed to build Docker image for '$SERVICE_NAME'"
    exit 1
fi

# 2. Tag and Push Docker Image (Optional, for production readiness)
# Replace with actual registry login and push commands

# docker tag "$SERVICE_NAME:$IMAGE_TAG" "$IMAGE_REGISTRY/$SERVICE_NAME:$IMAGE_TAG"
# docker push "$IMAGE_REGISTRY/$SERVICE_NAME:$IMAGE_TAG"
# if [ $? -ne 0 ]; then
#     echo "❌ Failed to push Docker image to registry."
#     # Optionally continue with local image if registry is not critical for local testing
# fi

echo "Docker image built and optionally pushed."

# 3. Apply Kubernetes Manifests
echo "Applying Kubernetes deployment for '$SERVICE_NAME' in namespace '$KUBERNETES_NAMESPACE'..."
# Update image name in deployment.yaml before applying
sed -i "s|image: ${SERVICE_NAME}:latest|image: ${IMAGE_REGISTRY}/${SERVICE_NAME}:${IMAGE_TAG}|g" "$K8S_MANIFESTS_DIR/deployment.yaml"

kubectl apply -f "$K8S_MANIFESTS_DIR/deployment.yaml" -n "$KUBERNETES_NAMESPACE"
if [ $? -ne 0 ]; then
    echo "❌ Failed to apply Kubernetes deployment for '$SERVICE_NAME'"
    exit 1
fi

echo "✓ FastAPI + Dapr service '$SERVICE_NAME' deployed to Kubernetes."

# Only this output enters agent context:
echo "✓ Service '$SERVICE_NAME' deployment initiated. Use verify.py to check status."
