#!/bin/bash
# Verify AGENTS.md structure for enterprise compliance

# Check if AGENTS.md exists
if [ ! -f "AGENTS.md" ]; then
    echo "❌ AGENTS.md not found. Please run generate_agents.sh first."
    exit 1
fi

echo "Verifying AGENTS.md for enterprise standards..."

# Check for required sections (enterprise specific)
REQUIRED_SECTIONS=(
    "# AGENTS.md"
    "## Repository Overview"
    "## Repository Structure"
    "## Skills Directory Structure"
    "## Skill Format Requirements"
    "### SKILL.md (What the AI Agent Loads)"
    "### Scripts/ Directory (What Actually Executes)"
    "### REFERENCE.md (Optional Deep Documentation)"
    "## Skill Examples"
    "## Skill Development Best Practices"
    "### Token Efficiency"
    "### Autonomous Development"
    "### Cross-Agent Compatibility"
    "## Usage Examples"
    "## Development Workflow"
    "## Success Criteria"
    "### Skill Autonomy ✅"
    "### Token Efficiency ✅"
    "### Cross-Agent Compatibility ✅"
    "### Architecture ✅"
    "## Quick Start"
    "## Resources"
    "## Frequently Asked Questions"
    "## Common Issues & Solutions"
)

ALL_SECTIONS_FOUND=true
for section in "${REQUIRED_SECTIONS[@]}"; do
    if ! grep -qF "$section" AGENTS.md; then
        echo "❌ Missing required section: \"$section\""
        ALL_SECTIONS_FOUND=false
    fi
done

if [ "$ALL_SECTIONS_FOUND" = true ]; then
    echo "✅ All required enterprise sections found in AGENTS.md"
else
    echo "❌ Some required enterprise sections are missing in AGENTS.md"
    exit 1
fi

# Check for placeholder replacement
if grep -q "\[Repository Name\]" AGENTS.md || grep -q "\[brief description of what's in this repo\]" AGENTS.md; then
    echo "⚠️ Warning: Placeholders '[Repository Name]' or '[brief description of what\'s in this repo]' still found in AGENTS.md. Run customize_agents.sh."
fi

# Check for correct Opencode directory reference
if grep -q "\.opencode/skills/" AGENTS.md; then
    echo "✅ Correct .opencode/skills/ reference found"
else
    echo "❌ Incorrect or missing .opencode/skills/ reference"
    exit 1
fi

# Only this output enters agent context:
echo "✓ AGENTS.md structure verified for enterprise standards"
