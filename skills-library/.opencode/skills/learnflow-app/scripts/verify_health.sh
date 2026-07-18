#!/bin/bash
# Verify health endpoint returns 200
echo "Testing LearnFlow health endpoint..."
# Build the Docker image if not built
docker build -t learnflow-app:latest /home/ali-hamza/Documents/Projects/Hackathon3/learnflow-app/src/
# Run container in background
docker run -d -p 8000:8000 --name learnflow-test learnflow-app:latest
# Wait for container to be ready
sleep 5
# Query health endpoint
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ "$response" = "200" ]; then
    echo "✓ Health check passed"
else
    echo "✗ Health check failed with status $response"
    exit 1
fi
# Clean up container
docker stop learnflow-test
docker rm learnflow-test
echo "Health verification completed."