#!/bin/bash
# Verify Helm deployment and test hook
echo "Verifying LearnFlow deployment..."
helm status learnflow-app >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "✗ Helm release not found"
    exit 1
fi
echo "✓ Helm release is installed"

# Run helm test hook
helm test learnflow-app --timeout 60s
if [ $? -ne 0 ]; then
    echo "✗ Helm test hook failed"
    exit 1
fi
echo "✓ Helm test hook passed"
echo "Deployment verification completed."