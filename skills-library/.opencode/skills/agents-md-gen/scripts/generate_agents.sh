#!/bin/bash
# Generate AGENTS.md files for AI agent development

# Create AGENTS.md template
cat > AGENTS.md << 'EOF'
# AGENTS.md

This document describes the structure, conventions, and guidelines for the [Repository Name] repository so AI agents can understand how to work with it.

## Repository Overview

This repository contains [brief description of what's in this repo].

## Repository Structure

```
[directory structure here]
```

## Skills Directory Structure

All skills follow the same pattern for maximum efficiency and reusability:

```
.claude/skills/
├── skill-name/
│   ├── SKILL.md              # Instructions (~100 tokens)
│   ├── REFERENCE.md          # Deep docs (on-demand)
│   └── scripts/               # Code execution (0 tokens)
└── ...  (available skills)
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
```

### Scripts/ Directory (What Actually Executes)
- **Token Budget**: 0 tokens (executed, not loaded)
- **Purpose**: Do the actual work outside the AI agent's context window
- **Output**: Minimal result returns to AI agent

### REFERENCE.md (Optional Deep Documentation)
- **Token Budget**: 0 tokens loaded on-demand
- **Purpose**: Deep technical details loaded only when needed

## Available Skills

List and describe the skills available in this repository.

## Quick Start

```bash
# Test with a skill
claude "deploy [functionality] using [skill-name] skill"

# Generate AGENTS.md
claude "create AGENTS.md for this repository using agents-md-gen skill"
```

## Success Criteria

### Skills Autonomy ✅
- AI goes from single prompt to running K8s deployment
- Zero manual intervention required
- Scripts execute outside agent context

### Token Efficiency ✅
- Skills use scripts for execution
- Minimal context window consumption
- 80-98% token reduction vs direct MCP

### Cross-Agent Compatibility ✅
- Same skill works on Claude Code
- Same skill works on Goose
- Both agents can use .claude/skills/ directory

## Getting Started

1. **Install Prerequisites**: Docker, Minikube, Helm, Claude Code, Goose
2. **Test a Skill**: Use agents-md-gen skill to generate AGENTS.md
3. **Deploy Infrastructure**: Test kafka-k8s-setup or postgres-k8s-setup
4. **Build Applications**: Use fastapi-dapr-agent, nextjs-k8s-deploy
5. **Complete LearnFlow**: Build the full AI tutoring platform

## Resources

### Official Documentation
- [AAIF Standards](https://aaif.io/)
- [Claude Code Skills](https://code.claude.com/docs/en/skills)
- [Goose Documentation](https://block.github.io/goose/)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [Dapr](https://dapr.io)
- [Kubernetes](https://kubernetes.io/docs/)
- [Helm](https://helm.sh/docs/)
- [Minikube](https://minikube.sigs.k8s.io/docs/)

### Hackathon Resources
- [AAIF Announcement](https://www.youtube.com/watch?v=8WdO7U3KASo)
- [Skills vs Agents](https://www.youtube.com/watch?v=CEvIs9y1uog)
- [MCP Code Execution](https://www.anthropic.com/engineering/code-execution-with-mcp)

## Frequently Asked Questions

**Q: What's the difference between traditional development and agentic development?**
**A**: Traditional: You write code → Code runs → Application works. Agentic: You write Skills → AI learns patterns → AI writes code → Application works.

**Q: Do I need to build both Claude Code and Goose versions?**
**A**: Yes! This demonstrates your skills are truly portable. Since Goose reads .claude/skills/ directly, the same skills work on both agents.

**Q: How much should the AI do vs. manual coding?**
**A**: Aim for maximum autonomy! Your evaluation score increases when AI agents can complete tasks with minimal manual intervention. The gold standard is single-prompt-to-deployment.

Good luck, Engineers! It's time to stop writing code and start teaching machines how to build systems autonomously.
EOF

# Create customization script
cat > scripts/customize_agents.sh << 'EOF'
#!/bin/bash
# Customize AGENTS.md for specific repository

REPO_NAME="$1"
REPO_DESCRIPTION="$2"
if [ -z "$REPO_NAME" ] || [ -z "$REPO_DESCRIPTION" ]; then
    echo "Usage: $0 <repository-name> <repository-description>"
    echo "Example: $0 skills-library 'Skills for teaching AI agents'"
    exit 1
fi

# Replace placeholders in AGENTS.md
sed -i "s/\[Repository Name\]/$REPO_NAME/g" AGENTS.md
sed -i "s/\[brief description of what's in this repo\]/$REPO_DESCRIPTION/g" AGENTS.md

# Only this output enters agent context:
echo "✓ AGENTS.md customized for $REPO_NAME repository"
EOF

# Create verification script
cat > scripts/verify_agents.sh << 'EOF'
#!/bin/bash
# Verify AGENTS.md structure

# Check if AGENTS.md exists
if [ ! -f "AGENTS.md" ]; then
    echo "✗ AGENTS.md not found"
    exit 1
fi

# Check for required sections
if ! grep -q "# AGENTS.md" AGENTS.md; then
    echo "✗ Missing AGENTS.md title"
    exit 1
fi

if ! grep -q "Repository Overview" AGENTS.md; then
    echo "✗ Missing Repository Overview section"
    exit 1
fi

# Check for repository structure example
if ! grep -q "```" AGENTS.md; then
    echo "✗ Missing directory structure example"
    exit 1
fi

# Check for skills directory structure
if ! grep -q "skills/" AGENTS.md; then
    echo "✗ Missing skills directory description"
    exit 1
fi

# Only this output enters agent context:
echo "✓ AGENTS.md structure verified"
EOF

# Only this output enters agent context:
echo "✓ AGENTS.md files generated successfully"
