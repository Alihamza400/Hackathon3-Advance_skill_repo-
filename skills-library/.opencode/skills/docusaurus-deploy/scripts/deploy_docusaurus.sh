#!/bin/bash
# Deploy Docusaurus static site to Kubernetes

DOC_NAME="$1"
NAMESPACE="default"
DOCKER_IMAGE="nginx:alpine"

if [ -z "$DOC_NAME" ]; then
    echo "Usage: $0 <doc-name> [--namespace <namespace>]"
    echo "Example: $0 learnflow-docs --namespace production"
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

# Load build info
if [ -f "../.docusaurus-build-info" ]; then
    source ../.docusaurus-build-info
else
    echo "❌ Error: Build info not found. Please run build_docusaurus.sh first."
    exit 1
fi

# Ensure namespace exists
echo "Ensuring Kubernetes namespace '$NAMESPACE' exists..."
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

echo "Deploying Docusaurus site '$DOC_NAME' to Kubernetes in namespace '$NAMESPACE'..."

# Create a ConfigMap with the static site content
echo "Creating ConfigMap with static site content..."
kubectl create configmap "${DOC_NAME}-content" --from-file="$BUILD_DIR" -n "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

if [ $? -ne 0 ]; then
    echo "❌ Failed to create ConfigMap for '$DOC_NAME'."
    exit 1
fi

# Create deployment
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${DOC_NAME}
  namespace: ${NAMESPACE}
  labels:
    app: ${DOC_NAME}
    tier: frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ${DOC_NAME}
  template:
    metadata:
      labels:
        app: ${DOC_NAME}
        tier: frontend
    spec:
      containers:
      - name: nginx
        image: ${DOCKER_IMAGE}
        ports:
        - containerPort: 80
        volumeMounts:
        - name: site-content
          mountPath: /usr/share/nginx/html
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
          limits:
            memory: "128Mi"
            cpu: "100m"
      volumes:
      - name: site-content
        configMap:
          name: ${DOC_NAME}-content
EOF

# Create service
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: ${DOC_NAME}
  namespace: ${NAMESPACE}
  labels:
    app: ${DOC_NAME}
spec:
  selector:
    app: ${DOC_NAME}
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
  type: ClusterIP
EOF

echo "✓ Docusaurus site '$DOC_NAME' deployed to Kubernetes."

# Store deployment info
echo "DOC_NAME=$DOC_NAME" > ../.docusaurus-deployment-info
echo "NAMESPACE=$NAMESPACE" >> ../.docusaurus-deployment-info

# Only this output enters agent context:
echo "✓ Docusaurus site '$DOC_NAME' deployed to Kubernetes in namespace '$NAMESPACE'."