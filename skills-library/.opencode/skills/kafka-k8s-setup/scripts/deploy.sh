#!/bin/bash
# Enterprise Kafka deployment script

# Parse command line arguments
ENVIRONMENT="development"
MONITORING=false
SECURITY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --monitoring)
            MONITORING=true
            shift
            ;;
        --security)
            SECURITY=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Set up enterprise configuration
CLUSTER_NAME="kafka-cluster"
NAMESPACE="kafka"
REPLICAS=3
ZOO_REPLICAS=3
STORAGE_CLASS="standard"

# Create namespace with proper labels
echo "Creating namespace $NAMESPACE with enterprise labels..."
kubectl create namespace $NAMESPACE \
    --save-config \
    -o yaml | kubectl apply -f -
echo "✓ Namespace '$NAMESPACE' created with enterprise configuration"

# Add enterprise labels
kubectl label namespace $NAMESPACE \
    environment=$ENVIRONMENT \
    managed-by=opencode-skills \
    monitoring=enabled \
    security=enabled

# Add storage class for persistent volumes
if [ "$ENVIRONMENT" = "production" ]; then
    echo "Setting up enterprise storage class for production..."
    kubectl apply -f - << EOF
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: kafka-storage
  annotations:
    storageclass.kubernetes.io/is-default: "true"
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
  iopsPerGB: 3
  fsType: ext4
mountOptions:
  - nolrucache
reclaimPolicy: Retain
volumeBindingMode: Immediate
volumeExpansion:
  enabled: true
EOF
echo "✓ Enterprise StorageClass configured"
fi

# Deploy Helm chart with enterprise options
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Build Helm command with enterprise flags
HELM_CMD="helm install $CLUSTER_NAME bitnami/kafka --namespace $NAMESPACE"
HELM_CMD="$HELM_CMD --set replicaCount=$REPLICAS"
HELM_CMD="$HELM_CMD --set zookeeper.replicaCount=$ZOO_REPLICAS"
HELM_CMD="$HELM_CMD --set service.type=LoadBalancer"
HELM_CMD="$HELM_CMD --set metrics.prometheus.jmx.enabled=true"
HELM_CMD="$HELM_CMD --set metrics.prometheus.jvm.enabled=true"
HELM_CMD="$HELM_CMD --set persistence.enabled=true"
HELM_CMD="$HELM_CMD --set persistence.storageClass=$STORAGE_CLASS"
HELM_CMD="$HELM_CMD --set zookeeper.persistence.enabled=true"
HELM_CMD="$HELM_CMD --set zookeeper.persistence.storageClass=$STORAGE_CLASS"

if [ "$MONITORING" = true ]; then
    HELM_CMD="$HELM_CMD --set metrics.prometheus.serviceMonitor.enabled=true"
    HELM_CMD="$HELM_CMD --set metrics.prometheus.serviceMonitor.namespace=$NAMESPACE"
fi

if [ "$SECURITY" = true ]; then
    HELM_CMD="$HELM_CMD --set auth.clientSsl.enabled=true"
    HELM_CMD="$HELM_CMD --set auth.metricsReporter.securityContext.runAsUser=1000"
fi

echo "Deploying enterprise Kafka cluster..."
eval $HELM_CMD

if [ $? -eq 0 ]; then
    echo "✓ Enterprise Kafka cluster deployed successfully"
else
    echo "✗ Kafka deployment failed"
    exit 1
fi

# Wait for deployment with timeout
echo "Waiting for Kafka cluster to become ready..."
kubectl wait --namespace $NAMESPACE \
    --for=condition=ready pod \
    --selector=app.kubernetes.io/name=kafka \
    --timeout=600s

# Store deployment details for verification
echo "CLUSTER_NAME=$CLUSTER_NAME" > ../.kafka-deployment-info
echo "NAMESPACE=$NAMESPACE" >> ../.kafka-deployment-info
echo "ENVIRONMENT=$ENVIRONMENT" >> ../.kafka-deployment-info
echo "MONITORING=$MONITORING" >> ../.kafka-deployment-info
echo "SECURITY=$SECURITY" >> ../.kafka-deployment-info

echo "✓ Enterprise Kafka deployment complete"
