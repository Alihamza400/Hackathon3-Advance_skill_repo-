# Getting Started

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose (optional, for containerized deployment)
- Dapr CLI (for Dapr-based service invocation)

## Installation

### Backend

```bash
cd learnflow-app
python -m venv venv
source venv/bin/activate
pip install -r src/requirements.txt
```

### Frontend

```bash
cd learnflow-app/frontend
npm install
```

## Running Locally

### Start microservices

Each service runs independently. From the `services/` directory:

```bash
# Start Auth Service
cd services/auth && uvicorn main:app --port 8001 &

# Start Triage Agent
cd services/triage && uvicorn main:app --port 8002 &

# Start Concepts Agent
cd services/concepts && uvicorn main:app --port 8003 &

# Start Code Review Agent
cd services/code-review && uvicorn main:app --port 8004 &

# Start Debug Agent
cd services/debug && uvicorn main:app --port 8005 &

# Start Exercise Agent
cd services/exercise && uvicorn main:app --port 8006 &

# Start Progress Agent
cd services/progress && uvicorn main:app --port 8007 &

# Start API Gateway
cd services/gateway && uvicorn main:app --port 8000
```

### Start Frontend

```bash
cd learnflow-app/frontend
npm run dev
```

The application will be available at `http://localhost:3000` with the API gateway at `http://localhost:8000`.

## First Tutorial

1. Open the app in your browser
2. Register a new account via `/auth/register`
3. Log in and navigate to the learning dashboard
4. Select a topic (e.g., "variables") and begin the lesson
5. Try the triage agent by asking a question about Python
6. Generate exercises to practice your skills
