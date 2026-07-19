# 🧠 LearnFlow — AI-Powered Learning Platform

> **Hackathon 3: Reusable Intelligence & Cloud-Native Mastery**

[![Next.js](https://img.shields.io/badge/Next.js-14.1-black?logo=next.js)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)]()
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python)]()
[![OpenRouter](https://img.shields.io/badge/OpenRouter-LLM-FF6600?)]()
[![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?logo=kubernetes)]()
[![Dapr](https://img.shields.io/badge/Dapr-0D2192?logo=dapr)]()
[![License](https://img.shields.io/badge/License-MIT-green)]()

**LearnFlow** is a multi-agent AI learning platform that teaches Python programming through LLM-powered tutoring, dynamic exercise generation, real-time code debugging, and personalized progress tracking.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **AI Tutor Chat** | Ask any Python question — LLM generates explanations with code examples, analogies, and key points |
| ✏️ **Dynamic Exercises** | AI generates unique coding exercises for ANY topic at any difficulty level |
| 🔍 **Smart Debugging** | Paste error code — AI identifies root cause, suggests fixes, and explains concepts to review |
| 📊 **Progress Analytics** | Track mastery scores, streaks, completed topics, and personalized learning suggestions |
| 💻 **Live Code Editor** | Browser-based Monaco editor with sandboxed Python execution (5s timeout, 50MB limit) |
| 🧩 **Multi-Agent Architecture** | 8 specialized microservices coordinated via Dapr sidecars and Kafka event streaming |
| 🔐 **JWT Authentication** | Secure login/register with role-based access (student/teacher/admin) |
| 🚢 **Cloud-Native** | Docker Compose for local dev, Kubernetes + Helm for production, ArgoCD for GitOps |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     KUBERNETES CLUSTER                       │
│                                                              │
│  ┌──────────┐   ┌──────────────────────────────────────┐    │
│  │  Kong    │   │         FastAPI Microservices         │    │
│  │  API GW  │──▶│  ┌──────┐ ┌──────┐ ┌────────┐       │    │
│  │  :8000   │   │  │Auth  │ │Triage│ │Concepts│       │    │
│  └──────────┘   │  │:8001 │ │:8002 │ │:8003   │       │    │
│       │         │  ├──────┤ ├──────┤ ├────────┤       │    │
│  ┌────▼─────┐   │  │ Code │ │Debug │ │Exercise│       │    │
│  │  Next.js │   │  │Review│ │:8005 │ │:8006   │       │    │
│  │  :3000   │   │  │:8004 │ ├──────┤ ├────────┤       │    │
│  └──────────┘   │  │Progress│ │ LLM  │              │    │
│                 │  │:8007   │ │:8010 │              │    │
│                 │  └────────┘ └──────┘              │    │
│                 └──────────────────────────────────────┘    │
│                          │           │                      │
│                    ┌─────▼───────────▼─────┐                 │
│                    │       Dapr Sidecars    │                 │
│                    │  (State, PubSub, Config)│                │
│                    └─────┬───────────┬─────┘                 │
│                    ┌─────▼───────────▼─────┐                 │
│                    │  Kafka / Redis / PG    │                 │
│                    └───────────────────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
User Query → Next.js → Kong GW → Triage Agent (classifies)
    ├── "explain X"    → Concepts Agent → LLM Service → OpenRouter
    ├── "debug code"   → Debug Agent → LLM Service → OpenRouter
    ├── "generate ex"  → Exercise Agent → LLM Service → OpenRouter
    └── "my progress"  → Progress Agent → PostgreSQL
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 14, React 18, TypeScript, Tailwind CSS, Framer Motion, Monaco Editor |
| **Backend** | Python 3.12, FastAPI, Pydantic, httpx |
| **AI/LLM** | OpenRouter API (GPT-4o-mini), custom LLM service abstraction |
| **Infrastructure** | Docker, Kubernetes, Dapr, Kafka, PostgreSQL, Redis |
| **API Gateway** | Kong (production), FastAPI gateway (local dev) |
| **Auth** | JWT (HS256), bcrypt password hashing |
| **Observability** | Prometheus metrics, structured logging |
| **CI/CD** | GitHub Actions, ArgoCD, Helm, Kustomize |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- Docker & Docker Compose
- OpenRouter API key ([get one free](https://openrouter.ai/keys))

### Local Development

```bash
# 1. Clone and enter
git clone https://github.com/Alihamza400/Hackathon3-Advance_skill_repo-.git
cd Hackathon3/learnflow-app

# 2. Set up Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r services/requirements.txt

# 3. Set your OpenRouter API key
export OPENROUTER_API_KEY="sk-or-v1-..."

# 4. Start infrastructure (PostgreSQL + Redis)
docker compose up -d postgres redis

# 5. Start all microservices
./start_services.sh

# 6. Start frontend (separate terminal)
cd frontend
npm install
npm run dev

# 7. Open http://localhost:3000
```

### Using Docker Compose (Full Stack)

```bash
# Start everything with one command
docker compose up -d --build

# Services will be available at:
# - Frontend:  http://localhost:3000
# - Gateway:   http://localhost:8000
# - PostgreSQL: localhost:5432
# - Redis:     localhost:6379
```

---

## 📁 Project Structure

```
learnflow-app/
├── frontend/                        # Next.js 14 application
│   └── src/
│       ├── app/                     # Pages (App Router)
│       │   ├── page.tsx             #   Landing page
│       │   ├── login/               #   Authentication
│       │   ├── register/            #   Registration
│       │   ├── dashboard/           #   Student dashboard
│       │   ├── learn/               #   AI Chat + Concepts + Editor
│       │   ├── exercises/           #   Exercise generation
│       │   ├── progress/            #   Progress tracking
│       │   └── code-editor/         #   Standalone code sandbox
│       ├── components/
│       │   ├── ui/                  #   Reusable UI primitives
│       │   ├── layout/              #   App shell (Navbar, Sidebar)
│       │   ├── dashboard/           #   Dashboard widgets
│       │   ├── exercises/           #   Exercise components
│       │   └── learn/               #   Chat + Editor + Viewer
│       ├── lib/api.ts               #   API client (axios)
│       ├── hooks/useAuth.ts         #   Auth state (zustand)
│       └── types/index.ts           #   TypeScript definitions
│
├── services/                        # Python microservices
│   ├── gateway/main.py              # API gateway (port 8000)
│   ├── auth/main.py                 # JWT auth (port 8001)
│   ├── triage/main.py               # Query router (port 8002)
│   ├── concepts/main.py             # Concept explanations (port 8003)
│   ├── code-review/main.py          # Code quality analysis (port 8004)
│   ├── debug/main.py                # Error debugger (port 8005)
│   ├── exercise/main.py             # Exercise engine (port 8006)
│   ├── progress/main.py             # Progress tracker (port 8007)
│   ├── llm/main.py                  # LLM/OpenRouter proxy (port 8010)
│   └── shared/base.py               # Shared framework
│
├── .opencode/skills/                # AI agent skills
│   ├── concept-reasoner/            # Deep LLM explanations
│   ├── ai-exercise-engineer/        # Dynamic exercise generation
│   └── concept-speaker/             # TTS-formatted explanations
│
├── k8s/                             # Kubernetes manifests
│   ├── base/                        # Shared Kustomize base
│   └── overlays/                    # Environment overrides
│
├── infra/                           # Infrastructure configs
│   ├── dapr/                        # Dapr components
│   ├── kafka/                       # Kafka configuration
│   ├── kong/                        # Kong API gateway routes
│   └── argocd/                      # ArgoCD GitOps configs
│
├── docs/                            # Docusaurus documentation
├── docker-compose.yml               # Local orchestration
├── Dockerfile.service               # Multi-stage service build
├── start.sh                         # Dev startup script
└── AGENTS.md                        # AI agent guidelines
```

---

## 📡 API Overview

All services are proxied through the gateway at `http://localhost:8000`.

### Core Endpoints

| Method | Endpoint | Service | Description |
|--------|----------|---------|-------------|
| POST | `/auth/login` | Auth | Login with email/password |
| POST | `/auth/register` | Auth | Create account |
| GET | `/auth/me` | Auth | Get current user profile |
| POST | `/concepts/explain` | Concepts | Explain a concept (AI or static) |
| POST | `/llm/chat` | LLM | Free-form AI chat |
| POST | `/llm/explain` | LLM | Structured LLM explanation |
| POST | `/exercises/generate` | Exercise | Generate exercise (template) |
| POST | `/exercises/generate-ai` | Exercise | Generate exercise (AI dynamic) |
| POST | `/exercises/submit` | Exercise | Submit code for grading |
| POST | `/debug` | Debug | Analyze code errors |
| POST | `/debug/execute` | Debug | Run code in sandbox |
| GET | `/progress/dashboard` | Progress | Get student dashboard |

See [docs/api-reference.md](learnflow-app/docs/api-reference.md) for full API docs.

---

## 🤖 AI Agent Skills

This project includes **3 reusable skills** for AI coding agents (Claude Code, Goose):

| Skill | Purpose | Script |
|-------|---------|--------|
| **concept-reasoner** | Deep LLM explanations with Socratic reasoning & follow-up Q&A | `bash .opencode/skills/concept-reasoner/scripts/reason-concept.sh "topic" "level"` |
| **ai-exercise-engineer** | Generate coding exercises via LLM for ANY topic | `bash .opencode/skills/ai-exercise-engineer/scripts/generate-exercise.sh "topic" "difficulty"` |
| **concept-speaker** | Speech-optimized explanations for TTS engines | `bash .opencode/skills/concept-speaker/scripts/speak-concept.sh "topic" "level"` |

```bash
# Example: Generate an AI-powered exercise
bash .opencode/skills/ai-exercise-engineer/scripts/generate-exercise.sh "closures" "intermediate"

# Example: Explain a concept with reasoning
bash .opencode/skills/concept-reasoner/scripts/reason-concept.sh "decorators" "beginner"
```

---

## 🧪 Running Tests

```bash
# Frontend lint
cd frontend && npm run lint

# Backend lint
ruff check services/

# Full CI pipeline (GitHub Actions)
# See .github/workflows/ci.yml
```

---

## 🚢 Deployment

### Kubernetes (Kustomize)

```bash
kubectl apply -k k8s/overlays/dev/
```

### Helm

```bash
helm install learnflow-app infra/learnflow-app/helm/learnflow-app/ \
  --values infra/learnflow-app/helm/learnflow-app/values.yaml
```

### ArgoCD (GitOps)

Apply the ArgoCD Application manifest:
```bash
kubectl apply -f infra/argocd/learnflow-app.yaml
```

---

## 📊 Project Stats

| Metric | Value |
|--------|-------|
| Microservices | 8 (auth, triage, concepts, code-review, debug, exercise, progress, llm) |
| Frontend Pages | 9 (landing, login, register, dashboard, learn, exercises, progress, code-editor) |
| Skills | 3 (concept-reasoner, ai-exercise-engineer, concept-speaker) |
| Languages | Python (backend), TypeScript (frontend), YAML (infra) |
| Database | PostgreSQL 16 (primary), Redis 7 (cache) |
| Event Bus | Kafka + Dapr pub/sub |
| LLM Provider | OpenRouter (GPT-4o-mini) |

---

## 🧑‍💻 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -am 'Add my feature'`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

See [docs/contributing.md](learnflow-app/docs/contributing.md) for detailed guidelines.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  Built with ❤️ for <strong>Hackathon 3</strong><br>
  <em>"Reusable Intelligence & Cloud-Native Mastery"</em>
</p>
