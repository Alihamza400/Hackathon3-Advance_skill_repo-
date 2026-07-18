#!/bin/bash
# Deploy AGENTS.md to a specified repository location

TARGET_REPO_PATH="$1"

if [ -z "$TARGET_REPO_PATH" ]; then
    echo "Usage: $0 <target-repository-path>"
    echo "Example: $0 ../learnflow-app/docs"
    exit 1
fi

# Ensure AGENTS.md exists in the current skill directory
if [ ! -f "AGENTS.md" ]; then
    echo "❌ Error: AGENTS.md not found in the current skill directory. Please run generate_agents.sh first."
    exit 1
fi

# Ensure the target repository path exists
if [ ! -d "$TARGET_REPO_PATH" ]; then
    echo "❌ Error: Target repository path '$TARGET_REPO_PATH' does not exist."
    exit 1
fi

# Copy AGENTS.md to the target repository
cp AGENTS.md "$TARGET_REPO_PATH/AGENTS.md"

if [ $? -eq 0 ]; then
    echo "✓ AGENTS.md deployed to $TARGET_REPO_PATH"
else
    echo "❌ Failed to deploy AGENTS.md to $TARGET_REPO_PATH"
    exit 1
fi
