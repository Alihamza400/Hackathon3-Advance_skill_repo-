# AGENTS.md

This document describes the structure, conventions, and guidelines for the learnflow-app repository so AI agents can understand how to work with it.

## Repository Overview

This repository contains LearnFlow – multi-agent AI learning platform.

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

**All skills are stored under the `.opencode/skills/` directory.**

## Skill Format Requirements

## Skill Examples

## Skill Development Best Practices

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
```

### Scripts/ Directory (What Actually Executes)
- **Token Budget**: 0 tokens (executed, not loaded)
- **Purpose**: Do the actual work outside the AI agent's context window
- **Output**: Minimal result returns to AI agent

### REFERENCE.md (Optional Deep Documentation)
- **Token Budget**: 0 tokens loaded on-demand
- **Purpose**: Deep technical details loaded only when needed

## Quick Start

```bash
# Test with a skill
claude "deploy [functionality] using [skill-name] skill"

# Generate AGENTS.md
claude "create AGENTS.md for this repository using agents-md-gen skill"
```

## Success Criteria

### Token Efficiency
### Autonomous Development
### Cross-Agent Compatibility
### Usage Examples
### Development Workflow
### Architecture
### Architecture ✅

### Skill Autonomy ✅
### Token Efficiency ✅
### Cross-Agent Compatibility ✅

## Common Issues & Solutions
- [ ] Document known issues and resolutions

## Validation
- [ ] All checks pass

## Resources

## Available Skills

### `concept-reasoner` (`.opencode/skills/concept-reasoner/`)
Deep LLM-powered concept explanations with Socratic reasoning, analogies, code examples, and follow-up Q&A. Uses the LLM service's `/explain` and `/chat` endpoints.

### `ai-exercise-engineer` (`.opencode/skills/ai-exercise-engineer/`)
Generates dynamic programming exercises via LLM for ANY topic and difficulty. Produces starter code, test cases, hints, and solutions — no hardcoded templates.

### `concept-speaker` (`.opencode/skills/concept-speaker/`)
Speech-optimized concept explanations formatted for text-to-speech engines.

## Frequently Asked Questions

**Q: What's the difference between traditional development and agentic development?**
**A**: Traditional: You write code → Code runs → Application works. Agentic: You write Skills → AI learns patterns → AI writes code → Application works.

**Q: Do I need to build both Claude Code and Goose versions?**
**A**: Yes! This demonstrates your skills are truly portable. Since Goose reads .claude/skills/ directly, the same skills work on both agents.

**Q: How much should the AI do vs. manual coding?**
**A**: Aim for maximum autonomy! Your evaluation score increases when AI agents can complete tasks with minimal manual intervention. The gold standard is single-prompt-to-deployment.

Good luck, Engineers! It's time to stop writing code and start teaching machines how to build systems autonomously.