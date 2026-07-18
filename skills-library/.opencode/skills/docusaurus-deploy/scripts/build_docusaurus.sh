#!/bin/bash
# Build Docusaurus static site for production

DOC_NAME="$1"

if [ -z "$DOC_NAME" ]; then
    echo "Usage: $0 <doc-name>"
    echo "Example: $0 learnflow-docs"
    exit 1
fi

DOC_DIR="./docs/$DOC_NAME"

# Ensure documentation directory exists
if [ ! -d "$DOC_DIR" ]; then
    echo "❌ Error: Docusaurus site directory '$DOC_DIR' not found. Please run create_docusaurus.sh first."
    exit 1
fi

echo "Building Docusaurus site '$DOC_NAME' for production..."

cd "$DOC_DIR"

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm ci
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies."
        exit 1
    fi
fi

# Build the static site
echo "Building static site..."
npm run build
if [ $? -ne 0 ]; then
    echo "❌ Failed to build Docusaurus site."
    exit 1
fi

echo "✓ Docusaurus site '$DOC_NAME' built successfully."

# Verify build output
if [ -d "build" ]; then
    BUILD_SIZE=$(du -sh build | cut -f1)
    echo "✓ Build output created: build/ ($BUILD_SIZE)"
else
    echo "❌ Build output directory not found."
    exit 1
fi

# Store build info for deployment script
echo "DOC_NAME=$DOC_NAME" > ../.docusaurus-build-info
echo "BUILD_DIR=$DOC_DIR/build" >> ../.docusaurus-build-info

# Only this output enters agent context:
echo "✓ Docusaurus site '$DOC_NAME' built successfully. Ready for deployment."