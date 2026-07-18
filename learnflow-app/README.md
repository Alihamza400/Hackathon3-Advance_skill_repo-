# LearnFlow Application - Built with Skills

This repository contains the **LearnFlow AI-powered Python tutoring platform** built entirely using the Skills from Hackathon III.

## Repository Overview

This application demonstrates the power of **Agentic Development**:

- **You**: Create reusable Skills that teach AI agents how to build systems
- **AI Agents**: Claude Code and Goose use your Skills to build complex cloud-native applications autonomously

**Key Insight**: Your Skills become reusable knowledge that AI agents can apply to build many applications, not just one.

## Architecture Built with Skills

```
learnflow-app/
├── .claude/skills/              # Same skills directory used by both agents
│   └── (Skills imported from skills-library)
├── src/
│   ├── frontend/              # Next.js with Monaco Editor
│   ├── backend/               # FastAPI + Dapr microservices
│   ├── infrastructure/        # Kubernetes manifests
│   └── mcp-servers/           # MCP servers for AI context
├── docs/                       # Generated documentation
└── README.md
```

**LearnFlow Platform Architecture**:
```
KUBERNETES CLUSTER
├── Next.js + Monaco (Frontend)
│   * User interface with embedded code editor
│   * Real-time code execution sandbox
│   * Progress tracking dashboard
├── FastAPI + Dapr (Microservices)
│   ├── Triage Agent (Routes queries)
│   ├── Concepts Agent (Explains Python)
│   ├── Code Review Agent (PEP 8 validation)
│   ├── Debug Agent (Error parsing)
│   ├── Exercise Agent (Generates/Grades)
│   └── Progress Agent (Tracks mastery)
├── Kafka (Event Streaming)
│   * Event-driven communication between services
│   * Lesson progress events
│   * Struggle alerts to teachers
├── PostgreSQL (Database)
│   * User data, progress, code submissions
│   * Mastery calculations
│   * Exercise records
├── Kong API Gateway (Auth)
│   * Routes traffic and handles JWT
│   * User authentication
│   * Role-based access control
└── MCP Servers (Context)
    * Database access for AI agents
    * Code execution sandbox
    * Progress monitoring tools
```

## How This Was Built

### Using Your Skills

This entire application was built using the **Skills** from the `skills-library` repository:

1. **Claude Code & Goose** used the same `.claude/skills/` directory
2. **Skills autonomously deployed** infrastructure (Kafka, PostgreSQL, microservices)
3. **Agentic development workflow**: You wrote Skills → AI built the application
4. **Zero manual coding**: Everything created by AI agents using your Skills

### Development Process

```bash
# Commit messages reflect agentic workflow:
"Claude: implemented Kafka consumer using kafka-k8s-setup skill"
"Goose: deployed PostgreSQL using postgres-k8s-setup skill"
"Claude: created FastAPI microservice using fastapi-dapr-agent skill"
"Goose: deployed Next.js frontend using nextjs-k8s-deploy skill"
```

## Skills Used to Build LearnFlow

### Infrastructure Skills
- **kafka-k8s-setup**: Deployed event streaming platform
- **postgres-k8s-setup**: Deployed user data database
- **k8s-foundation**: Basic Kubernetes operations

### Backend Skills  
- **fastapi-dapr-agent**: Created AI tutoring microservices
- **mcp-code-execution**: MCP servers with code execution

### Frontend Skills
- **nextjs-k8s-deploy**: Deployed Next.js with Monaco editor
- **docusaurus-deploy**: Generated documentation site

### AI Agent Skills
- **agents-md-gen**: Created development guidelines for AI agents

## Technical Specifications

### Python Curriculum
| Module | Topics Covered |
|--------|----------------|
| 1. Basics | Variables, Data Types, Input/Output, Operators, Type Conversion |
| 2. Control Flow | Conditionals, For/While Loops, Break/Continue |
| 3. Data Structures | Lists, Tuples, Dictionaries, Sets |
| 4. Functions | Defining Functions, Parameters, Return Values, Scope |
| 5. OOP | Classes & Objects, Attributes & Methods, Inheritance |
| 6. Files | Reading/Writing Files, CSV Processing, JSON Handling |
| 7. Errors | Try/Except, Exception Types, Custom Exceptions |
| 8. Libraries | Installing Packages, Working with APIs |

### AI Agent System
| Agent | Purpose & Capabilities |
|------|------------------------|
| **Triage Agent** | Routes queries: "explain" → Concepts, "error" → Debug |
| **Concepts Agent** | Explains Python concepts with examples, adapts to level |
| **Code Review Agent** | Analyzes correctness, PEP 8 style, efficiency, readability |
| **Debug Agent** | Parses errors, identifies root causes, provides hints |
| **Exercise Agent** | Generates and auto-grades coding challenges |
| **Progress Agent** | Tracks mastery scores and provides progress summaries |

### Business Rules

#### Mastery Calculation
```
Topic Mastery = weighted average of:
- Exercise completion: 40%
- Quiz scores: 30%
- Code quality ratings: 20%  
- Consistency (streak): 10%
```

#### Struggle Detection Triggers
- Same error type 3+ times
- Stuck on exercise > 10 minutes
- Quiz score < 50%
- Student says "I don't understand" or "I'm stuck"
- 5+ failed code executions in a row

#### Code Execution Sandbox
- Timeout: 5 seconds | Memory: 50MB
- No file system access (except temp) | No network access
- Allowed imports: standard library only (MVP)

### Demo Scenario

**Student Maya** logs in → Dashboard shows: "Module 2: Loops - 60% complete"

**Step 1**: Maya asks: "How do for loops work in Python?"

**Step 2**: Concepts Agent explains with code examples and visualizations

**Step 3**: Maya writes a for loop in Monaco editor, runs it successfully

**Step 4**: Agent offers a quiz → Maya gets 4/5 → Mastery updates to 68%

**Struggle Detection Example**:
- **Student James** struggles with list comprehensions
- Gets 3 wrong answers → Triggers struggle alert
- Alert sent to teacher Mr. Rodriguez
- Teacher views James's code attempts, types: "Create easy exercises on list comprehensions"
- Exercise Agent generates exercises → Teacher assigns with one click
- James receives notification → Completes exercises → Confidence restored

## Evaluation Criteria (Same as Skills Library)

| Criterion | Weight | Gold Standard |
|-----------|--------|---------------|
| **Skills Autonomy** | 15% | AI goes from single prompt to running K8s deployment |
| **Token Efficiency** | 10% | Skills use scripts for execution |
| **Cross-Agent Compatibility** | 5% | Same skill works on Claude Code AND Goose |
| **Architecture** | 20% | Correct Dapr patterns, Kafka pub/sub, stateless microservices |
| **MCP Integration** | 10% | MCP server provides rich context for debugging |
| **Documentation** | 10% | Comprehensive Docusaurus site deployed via Skills |
| **Spec-Kit Plus Usage** | 15% | High-level specs translate cleanly to agentic instructions |
| **LearnFlow Completion** | 15% | Application built entirely via skills |

## Directory Structure Details

### Frontend (Next.js + Monaco)
```
learnflow-app/src/frontend/
├── components/
│   ├── code-editor/
│   ├── progress-dashboard/
│   └── learning-interface/
├── pages/
│   ├── dashboard.js
│   ├── lesson.js
│   └── teacher.js
└── public/
    └── manifest.json
```

### Backend (FastAPI + Dapr)
```
learnflow-app/src/backend/
├── agents/
│   ├── triage-agent.py
│   ├── concepts-agent.py
│   ├── code-review-agent.py
│   ├── debug-agent.py
│   ├── exercise-agent.py
│   └── progress-agent.py
├── services/
│   ├── database-service.py
│   ├── kafka-service.py
│   └── auth-service.py
└── templates/
    ├── api-gateway.yaml
    └── service-templates/
```

### Infrastructure
```
learnflow-app/src/infrastructure/
├── kafka/
│   ├── kafka-deployment.yaml
│   └── kafka-service.yaml
├── postgres/
│   ├── postgres-deployment.yaml
│   └── postgres-service.yaml
├── dapr-components/
│   ├── components.yaml
│   └── sidecar-config/
└── ingress/
    └── kong-gateway.yaml
```

## Getting Started

### Prerequisites
- ✅ Skills library already built with required skills
- ✅ Docker, Minikube, Helm, Claude Code, Goose installed
- ✅ Both repositories created and verified

### Starting Development
```bash
# Navigate to learnflow-app
cd learnflow-app

# Test with a skill
claude "deploy Next.js frontend using nextjs-k8s-deploy skill"

# Build the complete application
claude "build the entire LearnFlow platform using all available skills"
```

### Key Features

1. **Real-time Code Execution**: Students write Python code and run it instantly
2. **Multi-Agent Architecture**: Specialized AI agents for different tutoring needs  
3. **Progress Tracking**: Mastery scores and struggle detection
4. **Teacher Dashboard**: Monitor student progress and generate exercises
5. **Event-Driven Architecture**: Kafka for real-time communication
6. **Container Orchestration**: Kubernetes for production deployment

## Success Metrics

### Skills Autonomy ✅
- All infrastructure deployed via Skills autonomously
- Single-prompt-to-deployment for complex applications
- Zero manual intervention for core functionality

### Cross-Agent Compatibility ✅
- Both Claude Code and Goose using same skills
- Consistent results across different AI agents
- Skills portable between agent environments

### Token Efficiency ✅
- Skills designed for minimal context window usage
- Scripts handle heavy processing outside agent context
- 80-98% token reduction vs direct MCP calls

### Architecture ✅
- Correct Dapr patterns for microservices
- Proper Kafka pub/sub implementation
- Stateless microservice design

## Future Extensions

### Bonus Skills (Can be developed later)
- **agent-testing-framework**: Automated testing for agent interactions
- **kafka-stream-processor**: Kafka stream processing applications
- **pg-data-backup-restore**: PostgreSQL backup and recovery
- **dapr-pubsub-binding**: Advanced Dapr patterns
- **mcp-state-management**: Durable state management
- **nextjs-perf-optimize**: Next.js performance optimization
- **docusaurus-search-config**: Documentation search optimization
- **prometheus-grafana-setup**: Monitoring setup
- **argocd-app-deployment**: GitOps deployment

## Resources

### LearnFlow Documentation
- **Generated Docs**: Docusaurus site deployed via Skills
- **API Documentation**: Auto-generated from FastAPI code
- **Architecture Guide**: LearnFlow design patterns

### Development Resources
- **Skills Library**: skills-library/ directory
- **Commit History**: Agentic workflow documentation
- **Testing**: Both agents used for development

## Good luck, Engineers!

The LearnFlow platform was built entirely using your Skills. By teaching AI agents how to build systems, you've created reusable knowledge that can build many applications, not just one.

**Remember**: Skills are the product. How they were developed (using agentic development) is the process judges will evaluate.

# End of LearnFlow Application Documentation
