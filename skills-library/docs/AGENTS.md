# AGENTS.md

This document describes the structure, conventions, and guidelines for the Hackathon III Skills Library repository so AI agents can understand how to work with it.

## Repository Overview

This repository contains **Skills** that teach AI coding agents (Claude Code and Goose) how to build cloud-native applications autonomously. The Skills are the product - the application built using these skills is just the demonstration.

## Repository Structure

```
skills-library/
├── .opencode/skills/
│   ├── agents-md-gen/
│   │   ├── SKILL.md              # Instructions (~100 tokens)
│   │   └── scripts/               # Code execution scripts (0 tokens)
│   ├── kafka-k8s-setup/
│   │   ├── SKILL.md              # Instructions (~100 tokens)
│   │   ├── REFERENCE.md          # Deep docs (loaded on-demand)
│   │   └── scripts/               # Code execution scripts (0 tokens)
│   ├── postgres-k8s-setup/
│   ├── fastapi-dapr-agent/
│   ├── mcp-code-execution/
│   ├── nextjs-k8s-deploy/
│   └── docusaurus-deploy/
├── docs/
│   └── skill-development-guide.md
└── README.md
```

## Skills Directory Structure

Each skill follows this exact pattern:

```
.skill-name/
├── SKILL.md              # Instructions for the AI agent
├── REFERENCE.md          # Optional: Deep technical documentation
└── scripts/
    ├── deploy.sh         # Main deployment/execution script
    ├── verify.py         # Verification script
    └── [other scripts]   # Additional utilities
```

## Skill Format Requirements

### SKILL.md (What the AI Agent Loads)
- **Token Budget**: ~100 tokens maximum
- **Format**: YAML frontmatter with instructions
- **Purpose**: Tell the AI agent WHAT to do

**Example Structure**:
```yaml
---
name: skill-name
description: Brief description of the skill
---

# Skill Instructions

## When to Use
- User asks for specific functionality

## Instructions
1. Run deployment script
2. Verify status
3. Confirm completion

## Validation
- [ ] All checks pass

See [REFERENCE.md](./REFERENCE.md) for configuration options.
```

### Scripts/ Directory (What Actually Executes)
- **Token Budget**: 0 tokens (executed, not loaded)
- **Purpose**: Do the actual work outside the AI agent's context window
- **Output**: Minimal result returns to AI agent

**Example scripts/deploy.sh**:
```bash
#!/bin/bash
# Execute Helm commands, API calls, etc.
helm install kafka bitnami/kafka --namespace kafka
# Only this output enters agent context:
echo "✓ Kafka deployed to namespace 'kafka'"
```

**Example scripts/verify.py**:
```python
#!/usr/bin/env python3
import subprocess, json, sys

result = subprocess.run(["kubectl", "get", "pods", "-n", "kafka"], capture_output=True, text=True)
# Only minimal result enters context:
if "Running" in result.stdout:
    print("✓ All pods running")
    sys.exit(0)
else:
    print("✗ Verification failed")
    sys.exit(1)
```

### REFERENCE.md (Optional Deep Documentation)
- **Token Budget**: 0 tokens loaded on-demand
- **Purpose**: Deep technical details loaded only when needed
- **Trigger**: AI agent explicitly requests more information

## Skill Examples

### 1. agents-md-gen
**Purpose**: Teaches AI agents how to create AGENTS.md files
**Must Include**: SKILL.md + script for AGENTS.md generation

### 2. kafka-k8s-setup  
**Purpose**: Deploy Apache Kafka on Kubernetes
**Must Include**: SKILL.md + deploy script + verify script

### 3. postgres-k8s-setup
**Purpose**: Deploy PostgreSQL on Kubernetes  
**Must Include**: SKILL.md + migration scripts

### 4. fastapi-dapr-agent
**Purpose**: Create FastAPI + Dapr microservices
**Must Include**: SKILL.md + templates

### 5. mcp-code-execution
**Purpose**: MCP with code execution pattern
**Must Include**: SKILL.md + Python scripts

### 6. nextjs-k8s-deploy
**Purpose**: Deploy Next.js applications
**Must Include**: SKILL.md + Dockerfile templates

### 7. docusaurus-deploy
**Purpose**: Deploy documentation sites
**Must Include**: SKILL.md + deploy scripts

## Skill Development Best Practices

### Token Efficiency
- **Goal**: 80-98% token reduction vs direct MCP
- **Strategy**: Wrap MCP in Skills + Scripts
- **Budget**: ~110 total tokens vs 50,000+ with direct MCP

### Autonomous Development
- **Testing**: Each skill tested with both Claude Code and Goose
- **Validation**: Skills work autonomously (single prompt to deployment)
- **Compatibility**: Same skills work on both agents

### Code Execution Pattern
1. **SKILL.md**: Tells the AI agent WHAT to do (~100 tokens)
2. **scripts/*.py**: Does the heavy lifting (0 tokens - executed)
3. **REFERENCE.md**: Deep docs loaded only when needed (0 tokens)
4. **Final Output**: Minimal result returns to context (~10 tokens)

## Usage Examples

### Deploying Kafka using Skills
```
Claude: Deploy Kafka on Kubernetes using kafka-k8s-setup skill
→ Agent loads .claude/skills/kafka-k8s-setup/SKILL.md (~100 tokens)
→ Agent executes .claude/skills/kafka-k8s-setup/scripts/deploy.sh (0 tokens)
→ Agent runs .claude/skills/kafka-k8s-setup/scripts/verify.py (0 tokens)  
→ Result: "✓ Kafka deployed to namespace 'kafka'" (~10 tokens)
```

### Scaling Architecture
- **Agentic vs Traditional**: Skills enable reuse across many applications
- **MCP Optimization**: Wrap tools in Skills to minimize context window usage
- **Cross-Agent Compatibility**: Same skills work on Claude Code AND Goose

## Development Workflow

1. **Create Skill**: Write SKILL.md + scripts (following token budget)
2. **Test with Claude**: Verify autonomous deployment
3. **Test with Goose**: Confirm cross-agent compatibility  
4. **Validate**: Ensure single-prompt-to-deployment works
5. **Document**: Update skills in learnflow-app via Skills

## Success Criteria

### Skill Autonomy ✅
- AI goes from single prompt to running K8s deployment
- Zero manual intervention required
- Scripts execute outside agent context

### Token Efficiency ✅
- Skills use scripts for execution
- MCP calls wrapped efficiently
- Minimal context window consumption

### Cross-Agent Compatibility ✅
- Same skill works on Claude Code
- Same skill works on Goose  
- Both agents can use .claude/skills/ directory

### Architecture ✅
- Correct Dapr patterns
- Kafka pub/sub messaging
- Stateless microservice principles

## Quick Start

```bash
# Test a skill
claude "deploy Kafka using kafka-k8s-setup skill"

# Generate AGENTS.md
claude "create AGENTS.md for this repository"

# Deploy infrastructure
claude "deploy postgres-k8s-setup skill"
```

Good luck, Engineers! It's time to stop writing code and start teaching machines how to build systems autonomously.
