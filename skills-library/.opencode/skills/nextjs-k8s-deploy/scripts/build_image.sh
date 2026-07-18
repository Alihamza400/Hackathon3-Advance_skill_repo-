#!/bin/bash
# Build Docker image for Next.js application

APP_NAME="$1"
IMAGE_REGISTRY="your-docker-registry.io" # Replace with your actual registry
IMAGE_TAG="latest" # Can be dynamically generated, e.g., from git commit SHA

if [ -z "$APP_NAME" ]; then
    echo "Usage: $0 <app-name>"
    echo "Example: $0 learnflow-frontend"
    exit 1
}

APP_DIR="./apps/$APP_NAME"

# Ensure application directory and Dockerfile exist
if [ ! -d "$APP_DIR" ] || [ ! -f "$APP_DIR/Dockerfile" ]; then
    echo "❌ Error: Next.js application directory or Dockerfile not found at '$APP_DIR'. Please run create_config.sh first."
    exit 1
}

echo "Building Docker image for Next.js app '$APP_NAME' with tag '$IMAGE_TAG'..."

# Build the Docker image
docker build -t "$APP_NAME:$IMAGE_TAG" -f "$APP_DIR/Dockerfile" "$APP_DIR"
if [ $? -ne 0 ]; then
    echo "❌ Failed to build Docker image for '$APP_NAME'"
    exit 1
}

echo "✓ Docker image '$APP_NAME:$IMAGE_TAG' built successfully."

# Optionally tag and push the image to a registry for production deployments
# Uncomment and configure these lines for your CI/CD pipeline
# if [ ! -z "$IMAGE_REGISTRY" ]; then
#     echo "Tagging and pushing image to registry '$IMAGE_REGISTRY'..."
#     docker tag "$APP_NAME:$IMAGE_TAG" "$IMAGE_REGISTRY/$APP_NAME:$IMAGE_TAG"
#     if [ $? -ne 0 ]; then
#         echo "❌ Failed to tag image."
#         exit 1
#     fi
#     docker push "$IMAGE_REGISTRY/$APP_NAME:$IMAGE_TAG"
#     if [ $? -ne 0 ]; then
#         echo "❌ Failed to push image to registry."
#         exit 1
#     fi
#     echo "✓ Image pushed to '$IMAGE_REGISTRY/$APP_NAME:$IMAGE_TAG'."
# fi

# Store image info for subsequent scripts (e.g., Helm chart generation)
echo "APP_NAME=$APP_NAME" > ../.nextjs-image-info
echo "IMAGE_TAG=$IMAGE_TAG" >> ../.nextjs-image-info
echo "IMAGE_REGISTRY=$IMAGE_REGISTRY" >> ../.nextjs-image-info

# Only this output enters agent context:
echo "✓ Next.js Docker image '$APP_NAME:$IMAGE_TAG' built and ready."
