#!/bin/bash
# Bootstrap LearnFlow AI platform
echo "Bootstrapping LearnFlow platform..."
echo "Creating virtual environment..."
python3 -m venv venv
echo "Activating virtual environment..."
source venv/bin/activate
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r /home/ali-hamza/Documents/Projects/Hackathon3/learnflow-app/src/requirements.txt
echo "Building Docker image..."
docker build -t learnflow-app:latest /home/ali-hamza/Documents/Projects/Hackathon3/learnflow-app/src/
echo "Bootstrap completed."