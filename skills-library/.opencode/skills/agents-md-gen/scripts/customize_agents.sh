#!/bin/bash
# Customize AGENTS.md for specific repository

REPO_NAME="$1"
REPO_DESCRIPTION="$2"

if [ -z "$REPO_NAME" ] || [ -z "$REPO_DESCRIPTION" ]; then
    echo "Usage: $0 <repository-name> <repository-description>"
    echo "Example: $0 skills-library 'Skills for teaching AI agents'"
    exit 1
fi

# Ensure AGENTS.md exists before attempting to customize
if [ ! -f "AGENTS.md" ]; then
    echo "❌ Error: AGENTS.md not found in the current directory. Please run generate_agents.sh first."
    exit 1
fi

# Replace placeholders in AGENTS.md using sed
sed -i "s/\[Repository Name\]/$REPO_NAME/g" AGENTS.md
sed -i "s/\[brief description of what's in this repo\]/$REPO_DESCRIPTION/g" AGENTS.md

# Only this output enters agent context:
echo "✓ AGENTS.md customized for $REPO_NAME repository"
