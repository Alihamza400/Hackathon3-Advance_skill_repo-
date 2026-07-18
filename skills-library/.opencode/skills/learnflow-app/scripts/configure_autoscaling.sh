#!/bin/bash
# Configure autoscaling for LearnFlow
echo "Configuring autoscaling for LearnFlow..."
echo "Applying Horizontal Pod Autoscaler..."
kubectl autoscale deployment learnflow-app --cpu-percent=80 --min=3 --max=15
echo "Autoscaling configuration applied."