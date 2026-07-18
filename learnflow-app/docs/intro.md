# Introduction to LearnFlow

## What is LearnFlow?

LearnFlow is a multi-agent AI learning platform that provides personalized coding education through intelligent tutoring. It uses a distributed microservices architecture with specialized AI agents to deliver concept explanations, code reviews, debugging assistance, exercises, and progress tracking.

## Architecture Overview

LearnFlow employs a **multi-agent AI system** where each agent is a dedicated microservice handling a specific domain of the learning experience:

- **API Gateway** — Central entry point, routes requests, handles auth, rate limiting
- **Triage Agent** — Classifies student queries and routes them to the appropriate specialist agent
- **Concepts Agent** — Explains Python concepts at various difficulty levels
- **Code Review Agent** — Reviews code for quality, security, performance, and best practices
- **Debug Agent** — Analyzes errors and provides debugging hints with sandboxed code execution
- **Exercise Agent** — Generates and grades coding exercises
- **Progress Agent** — Tracks student progress, mastery scores, and streaks
- **Auth Service** — Manages authentication, authorization, and user management

The agents communicate via Dapr (Distributed Application Runtime) for service invocation and event-driven communication.

## Quick Start

```bash
# 1. Clone the repository
git clone <repository-url>
cd learnflow-app

# 2. Install dependencies
pip install -r src/requirements.txt

# 3. Run services (from project root)
# See getting-started.md for detailed instructions
```
