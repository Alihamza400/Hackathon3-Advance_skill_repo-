# Hackathon III Skills Library

This repository contains **Skills** that teach AI coding agents (Claude Code and Goose) how to build cloud-native applications autonomously. The Skills are the product - the application built using these skills is just the demonstration.

## Repository Overview

This repository is designed to demonstrate the **Agentic Development** paradigm:

- **Traditional Development**: You write code → Code runs → Application works
- **Agentic Development**: You write Skills → AI learns patterns → AI writes code → Application works

**Key Insight**: Your skills can be reused to build many applications, not just one.

## Skills Directory Structure

All skills follow the same pattern for maximum efficiency and reusability:

```
.skills-library/
├── .opencode/skills/
│   ├── skill-name/
│   │   ├── SKILL.md              # Instructions (~100 tokens)
│   │   ├── REFERENCE.md          # Deep docs (on-demand)
│   │   └── scripts/               # Code execution (0 tokens)
│   └── ...  (7 core skills)
├── docs/
│   └── skill-development-guide.md
└── README.md
```

## The Skills Pattern

Each skill uses the **MCP Code Execution** pattern for maximum token efficiency:

- **SKILL.md**: Tells the AI agent WHAT to do (~100 tokens)
- **scripts/*.py**: Does the heavy lifting (0 tokens - executed, not loaded)
- **REFERENCE.md**: Deep docs loaded only when needed (0 tokens)
- **Final Output**: Minimal result returns to context (~10 tokens)

**Result**: 80-98% token reduction vs direct MCP calls!

## Core Skills (7 Required)

### 1. agents-md-gen
**Purpose**: Teaches AI agents how to create AGENTS.md files
**Gold Standard**: AI agents generate valid AGENTS.md from a single prompt

### 2. kafka-k8s-setup
**Purpose**: Deploy Apache Kafka on Kubernetes with Helm
**Must Include**: SKILL.md + deploy script + verify script

### 3. postgres-k8s-setup  
**Purpose**: Deploy PostgreSQL on Kubernetes with Helm
**Must Include**: SKILL.md + migration scripts

### 4. fastapi-dapr-agent
**Purpose**: Create FastAPI + Dapr microservices
**Must Include**: SKILL.md + templates

### 5. mcp-code-execution
**Purpose**: Demonstrates MCP with code execution pattern
**Must Include**: SKILL.md + Python scripts

### 6. nextjs-k8s-deploy
**Purpose**: Deploy Next.js applications on Kubernetes
**Must Include**: SKILL.md + Dockerfile templates

### 7. docusaurus-deploy
**Purpose**: Deploy Docusaurus documentation sites
**Must Include**: SKILL.md + deploy scripts

## Skill Development Best Practices

### Token Efficiency
- **Budget**: ~100 tokens per SKILL.md
- **Strategy**: Scripts handle processing (0 tokens)
- **Result**: Only minimal output enters agent context
- **Goal**: 80-98% token reduction vs direct MCP

### Autonomous Development
- **Testing**: Each skill tested with both Claude Code AND Goose
- **Validation**: Skills work autonomously (single prompt to deployment)
- **Compatibility**: Same skills work on both agents

### Cross-Agent Compatibility
- **Claude Code**: Proprietary, cloud-first, code-centric
- **Goose**: Open-source, local-first, LLM-agnostic
- **Skill Standard**: Works on both without modification

## Quick Start Checklist

### Phase 1: Setup
1. ✅ Install prerequisites (Docker, Minikube, Helm, Claude Code, Goose)
2. ✅ Run verification script
3. ✅ Create both repositories

### Phase 2: Foundation Skills
- ✅ agents-md-gen: Create AGENTS.md files
- ✅ k8s-foundation: Basic cluster health checks

### Phase 3: Infrastructure Skills
- ✅ kafka-k8s-setup: Deploy Kafka
- ✅ postgres-k8s-setup: Deploy PostgreSQL

### Phase 4: Backend Services
- ✅ fastapi-dapr-agent: Create microservices

### Phase 5: Frontend
- ✅ nextjs-k8s-deploy: Deploy Next.js with Monaco editor

### Phase 6: Integration
- ✅ mcp-code-execution: MCP servers with code execution
- ✅ docusaurus-deploy: Documentation deployment

### Phase 7: LearnFlow Build
- ✅ Build complete application using skills

### Phase 8: Polish
- ✅ Complete documentation
- ✅ Demo ready
- ✅ Submit repositories

## Evaluation Criteria (Weighted)

| Criterion | Weight | Gold Standard |
|-----------|--------|---------------|
| **Skills Autonomy** | 15% | AI goes from single prompt to running K8s deployment, zero manual intervention |
| **Token Efficiency** | 10% | Skills use scripts for execution, MCP calls wrapped efficiently |
| **Cross-Agent Compatibility** | 5% | Same skill works on Claude Code AND Goose |
| **Architecture** | 20% | Correct Dapr patterns, Kafka pub/sub, stateless microservice principles |
| **MCP Integration** | 10% | MCP server provides rich context enabling AI to debug and expand system |
| **Documentation** | 10% | Comprehensive Docusaurus site deployed via Skills playbook |
| **Spec-Kit Plus Usage** | 15% | High-level specs translate cleanly to agentic instructions |
| **LearnFlow Completion** | 15% | Application built entirely via skills |

## Getting Started

### 1. Test with agents-md-gen (Simplest Skill)
```bash
# Check existing skills
ls .claude/skills/

# Test with Claude Code
claude "create AGENTS.md for this repository using agents-md-gen skill"

# Test with Goose  
goose "create AGENTS.md for this repository"
```

### 2. Test Infrastructure Skills
```bash
# Deploy Kafka
claude "deploy Kafka using kafka-k8s-setup skill"

# Deploy PostgreSQL
claude "deploy PostgreSQL using postgres-k8s-setup skill"
```

### 3. Complete LearnFlow Application
Build the complete AI-powered Python tutoring platform using your skills:

**Architecture Overview**:
```
KUBERNETES CLUSTER
├── Next.js + Monaco (Frontend)
├── FastAPI + Dapr (Microservices)
├── Kafka (Event Streaming)
├── PostgreSQL (Database)
├── Kong API Gateway (Auth)
└── MCP Servers (Context)
```

## Development Workflow

### 1. Create Skills
- Write SKILL.md with YAML frontmatter (max ~100 tokens)
- Create scripts for execution (0 tokens)
- Add REFERENCE.md for deep documentation (on-demand)
- Test with both Claude Code and Goose

### 2. Test Skills
- Verify autonomous deployment works
- Confirm cross-agent compatibility  
- Validate token efficiency targets
- Document changes made to improve skills

### 3. Build LearnFlow
- Use your skills to create the application
- Let AI agents build the actual code
- Focus on skill development, not manual coding

### 4. Submit
- Both repositories submitted via Google Form
- Commit history should reflect agentic workflow
- Skills are the product, development process is the process

## Gold Standards & Success Criteria

### Skills Autonomy ✅
- Single prompt → AI agent loads skill
- Skill scripts execute autonomously  
- Deployment completes with zero manual intervention

### Token Efficiency ✅
- Skills use scripts for MCP interaction
- Minimal context window consumption
- 80-98% reduction vs direct MCP calls

### Cross-Agent Compatibility ✅
- Same skills work on Claude Code
- Same skills work on Goose
- Both agents can use .claude/skills/ directory

### Architecture ✅
- Correct Dapr patterns for microservices
- Proper Kafka pub/sub messaging
- Stateless microservice principles

## Resources

### Official Documentation
- **AAIF Standards**: https://aaif.io/
- **Claude Code Skills**: https://code.claude.com/docs/en/skills
- **Goose Documentation**: https://block.github.io/goose/
- **Model Context Protocol**: https://modelcontextprotocol.io
- **Dapr**: https://dapr.io
- **Kubernetes**: https://kubernetes.io/docs/
- **Helm**: https://helm.sh/docs/
- **Minikube**: https://minikube.sigs.k8s.io/docs/

### Additional Resources
- **AAIF Announcement**: https://www.youtube.com/watch?v=8WdO7U3KASo
- **Skills vs Agents**: https://www.youtube.com/watch?v=CEvIs9y1uog
- **MCP Code Execution**: https://www.anthropic.com/engineering/code-execution-with-mcp

## Frequently Asked Questions

**Q: Do I need to build both Claude Code and Goose versions?**
**A**: Yes! This demonstrates your skills are truly portable. Since Goose reads .claude/skills/ directly, the same skills work on both agents.

**Q: What if Claude Code or Goose generates incorrect code?**
**A**: This is expected! The goal is to refine your skills until the AI generates correct code consistently. Document what changes you made to improve the skills.

**Q: Can I use other AI models besides Claude and Goose?**
**A**: Yes, you can use Claude Code Router to integrate Gemini or other APIs. However, Claude Code and Goose are required as the primary agents.

**Q: How much should the AI do vs. manual coding?**
**A**: Aim for maximum autonomy! Your evaluation score increases when AI agents can complete tasks with minimal manual intervention. The gold standard is single-prompt-to-deployment.

## Common Issues & Solutions

### Issue: Minikube won't start
**Symptoms**: "Exiting due to DRV_NOT_HEALTHY" or Docker errors
**Solution**: 
1. Ensure Docker Desktop is running
2. `minikube delete && minikube start --driver=docker`
3. If on Mac M1/M2: `minikube start --driver=docker --alsologtostderr`

### Issue: Helm chart installation fails
**Symptoms**: "no matches for kind" or version errors
**Solution**: 
1. `helm repo update`
2. `helm search repo bitnami/kafka --versions`
3. Find compatible version and install with: `helm install kafka bitnami/kafka --version X.Y.Z`

### Issue: Claude Code not recognizing Skills
**Symptoms**: Skill doesn't appear or isn't used
**Solution**:
1. Verify SKILL.md is in `.claude/skills/<name>/SKILL.md`
2. Check YAML frontmatter syntax (--- at start and end)
3. Run: `claude --debug` to see skill loading
4. Ensure allowed-tools are valid tool names

### Issue: Pods stuck in Pending state
**Symptoms**: `kubectl get pods` shows Pending for >5 minutes
**Solution**:
```bash
kubectl describe pod <pod-name>
# Check Events section for root cause

# Common causes:
# - Insufficient resources: Increase Minikube memory
# - PVC issues: Check storage class exists
# - Image pull: Verify image name and registry access
```

## Good luck, Engineers!

*It's time to stop writing code and start teaching machines how to build systems autonomously.*

## Disclaimer

The Skills are the product. How they were developed (using agentic development processes) is the process that judges will evaluate. Your goal: make your skills work autonomously to get in the winners queue!
