#!/bin/bash
# Deploy LearnFlow services
echo "Deploying LearnFlow services..."
echo "Building Docker image..."
docker build -t learnflow-app:latest /home/ali-hamza/Documents/Projects/Hackathon3/learnflow-app/src/
echo "Deploying to cluster via Helm..."
helm upgrade --install learnflow-app ./infra/learnflow-app/helm/learnflow-app \
  -f ./infra/learnflow-app/helm/learnflow-app/values-production.yaml
echo "Deployment completed."