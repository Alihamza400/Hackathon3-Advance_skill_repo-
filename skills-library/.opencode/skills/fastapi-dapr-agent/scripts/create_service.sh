#!/bin/bash
# Enterprise FastAPI + Dapr microservice creation script

SERVICE_NAME="$1"
ENVIRONMENT="development"

if [ -z "$SERVICE_NAME" ]; then
    echo "Usage: $0 <service-name> [--environment <env>]"
    echo "Example: $0 concepts-agent --environment production"
    exit 1
fi

while [[ $# -gt 0 ]]; do
    case $1 in
        --environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

SERVICE_DIR="./services/$SERVICE_NAME"
COMPONENTS_DIR="./components/$SERVICE_NAME"
K8S_MANIFESTS_DIR="./k8s-manifests/$SERVICE_NAME"

# Create service directories
mkdir -p "$SERVICE_DIR" "$COMPONENTS_DIR" "$K8S_MANIFESTS_DIR"

echo "Creating enterprise FastAPI service template '$SERVICE_NAME' in $SERVICE_DIR..."

# Create FastAPI main.py with Dapr integration
cat > "$SERVICE_DIR/main.py" << EOF
from fastapi import FastAPI, Depends, HTTPException
from dapr.clients import DaprClient
import uvicorn
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title=f"{SERVICE_NAME.replace("-", " ").title()} Agent Service")

DAPR_STORE_NAME = os.getenv("DAPR_STORE_NAME", "statestore")
DAPR_PUBSUB_NAME = os.getenv("DAPR_PUBSUB_NAME", "pubsub")

# Dapr client dependency
def get_dapr_client():
    with DaprClient() as dapr_client:
        yield dapr_client

@app.get("/")
async def root():
    logger.info(f"[{SERVICE_NAME}] Root endpoint hit.")
    return {"service": "$SERVICE_NAME", "status": "running", "environment": "$ENVIRONMENT"}

@app.get("/health")
async def health():
    logger.info(f"[{SERVICE_NAME}] Health check endpoint hit.")
    return {"status": "healthy"}

@app.post("/save_state/{key}")
async def save_state(key: str, value: dict, dapr_client: DaprClient = Depends(get_dapr_client)):
    try:
        logger.info(f"[{SERVICE_NAME}] Saving state for key: {key}")
        dapr_client.save_state(store_name=DAPR_STORE_NAME, key=key, value=json.dumps(value))
        return {"status": "success", "key": key}
    except Exception as e:
        logger.error(f"[{SERVICE_NAME}] Error saving state: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_state/{key}")
async def get_state(key: str, dapr_client: DaprClient = Depends(get_dapr_client)):
    try:
        logger.info(f"[{SERVICE_NAME}] Getting state for key: {key}")
        response = dapr_client.get_state(store_name=DAPR_STORE_NAME, key=key)
        if response.data:
            return json.loads(response.data)
        raise HTTPException(status_code=404, detail="State not found")
    except Exception as e:
        logger.error(f"[{SERVICE_NAME}] Error getting state: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/publish_event/{topic}")
async def publish_event(topic: str, data: dict, dapr_client: DaprClient = Depends(get_dapr_client)):
    try:
        logger.info(f"[{SERVICE_NAME}] Publishing to topic: {topic}")
        dapr_client.publish_event(pubsub_name=DAPR_PUBSUB_NAME, topic_name=topic, data=json.dumps(data))
        return {"status": "success", "topic": topic, "data": data}
    except Exception as e:
        logger.error(f"[{SERVICE_NAME}] Error publishing event: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Dapr pubsub subscription endpoint
@app.get("/dapr/subscribe")
async def subscribe():
    logger.info(f"[{SERVICE_NAME}] Dapr subscribe endpoint hit.")
    return [
        {
            "pubsubname": DAPR_PUBSUB_NAME,
            "topic": "learning.events", # Example topic
            "route": "/handle_learning_event"
        }
    ]

@app.post("/handle_learning_event")
async def handle_learning_event(event: dict):
    logger.info(f"[{SERVICE_NAME}] Received learning event: {event}")
    # Process the event here
    return {"status": "SUCCESS"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

# Create enterprise Dockerfile
cat > "$SERVICE_DIR/Dockerfile" << EOF
# Use an official Python runtime as a parent image
FROM python:3.10-slim-buster

# Set the working directory in the container
WORKDIR /app

# Install production dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Expose port 8000 for the FastAPI application
EXPOSE 8000

# Run the application using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# Create requirements.txt
cat > "$SERVICE_DIR/requirements.txt" << EOF
fastapi==0.111.0
uvicorn==0.29.0
dapr-client==1.11.0
pydantic==2.7.1
python-json-logger==2.0.7
EOF

# Create basic Kubernetes deployment manifest (Helm values will override this usually)
cat > "$K8S_MANIFESTS_DIR/deployment.yaml" << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${SERVICE_NAME}-deployment
  namespace: default
  labels:
    app: ${SERVICE_NAME}
    environment: ${ENVIRONMENT}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ${SERVICE_NAME}
  template:
    metadata:
      labels:
        app: ${SERVICE_NAME}
        environment: ${ENVIRONMENT}
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "${SERVICE_NAME}"
        dapr.io/app-port: "8000"
        dapr.io/config: "appconfig"
    spec:
      containers:
      - name: ${SERVICE_NAME}
        image: ${SERVICE_NAME}:latest # Placeholder, build script will push
        ports:
        - containerPort: 8000
        env:
        - name: DAPR_STORE_NAME
          value: "statestore"
        - name: DAPR_PUBSUB_NAME
          value: "pubsub"
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "250m"
EOF

# Create Dapr components configuration for Redis (assuming Redis is deployed via Helm)
cat > "$COMPONENTS_DIR/statestore.yaml" << EOF
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: default
spec:
  type: state.redis
  version: v1
  metadata:
  - name: redisHost
    value: "redis-master.default.svc.cluster.local:6379" # Assuming Redis Helm chart
  - name: redisPassword
    secretKeyRef:
      name: redis # Name of the Kubernetes secret
      key: redis-password # Key in the secret
EOF

cat > "$COMPONENTS_DIR/pubsub.yaml" << EOF
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
  namespace: default
spec:
  type: pubsub.redis
  version: v1
  metadata:
  - name: redisHost
    value: "redis-master.default.svc.cluster.local:6379"
  - name: redisPassword
    secretKeyRef:
      name: redis
      key: redis-password
EOF

# Only this output enters agent context:
echo "✓ Enterprise FastAPI + Dapr service template '$SERVICE_NAME' created with Dockerfile and K8s manifests"
