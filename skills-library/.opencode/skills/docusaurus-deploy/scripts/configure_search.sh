#!/bin/bash
# Configure search functionality for Docusaurus site (Algolia DocSearch)

DOC_NAME="$1"
ALGOLIA_APP_ID=""
ALGOLIA_API_KEY=""
ALGOLIA_INDEX_NAME=""

if [ -z "$DOC_NAME" ]; then
    echo "Usage: $0 <doc-name> [--algolia-app-id <id>] [--algolia-api-key <key>] [--algolia-index-name <name>]"
    echo "Example: $0 learnflow-docs --algolia-app-id ABC123 --algolia-api-key secret --algolia-index-name learnflow"
    exit 1
}

while [[ $# -gt 0 ]]; do
    case $1 in
        --algolia-app-id)
            ALGOLIA_APP_ID="$2"
            shift 2
            ;;
        --algolia-api-key)
            ALGOLIA_API_KEY="$2"
            shift 2
            ;;
        --algolia-index-name)
            ALGOLIA_INDEX_NAME="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

DOC_DIR="./docs/$DOC_NAME"

# Ensure documentation directory exists
if [ ! -d "$DOC_DIR" ]; then
    echo "❌ Error: Docusaurus site directory '$DOC_DIR' not found. Please run create_docusaurus.sh first."
    exit 1
fi

echo "Configuring search for Docusaurus site '$DOC_NAME'..."

if [ -z "$ALGOLIA_APP_ID" ] || [ -z "$ALGOLIA_API_KEY" ] || [ -z "$ALGOLIA_INDEX_NAME" ]; then
    echo "⚠️ Warning: Algolia credentials not provided. Skipping DocSearch configuration."
    echo "   You can run this script again with --algolia-app-id, --algolia-api-key, and --algolia-index-name."
    exit 0
fi

# Update docusaurus.config.js to include Algolia DocSearch
# This is a simplified approach - in practice you'd use a more robust config update method
CONFIG_FILE="$DOC_DIR/docusaurus.config.js"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Error: docusaurus.config.js not found in '$DOC_DIR'."
    exit 1
fi

# Create a backup
cp "$CONFIG_FILE" "$CONFIG_FILE.bak"

# Update the config to include Algolia DocSearch
# This uses sed to inject the algolia config into themeConfig
sed -i "/themeConfig:/a \
  algolia: {\n    appId: '$ALGOLIA_APP_ID',\n    apiKey: '$ALGOLIA_API_KEY',\n    indexName: '$ALGOLIA_INDEX_NAME',\n    contextualSearch: true,\n    externalUrlRegex: 'external\\.com|domain\\.com',\n  }," "$CONFIG_FILE"

if [ $? -eq 0 ]; then
    echo "✓ Algolia DocSearch configured in docusaurus.config.js"
else
    echo "❌ Failed to update docusaurus.config.js. Restoring backup."
    mv "$CONFIG_FILE.bak" "$CONFIG_FILE"
    exit 1
fi

# Remove backup
rm "$CONFIG_FILE.bak"

echo "✓ Search configured for Docusaurus site '$DOC_NAME' with Algolia DocSearch."
echo "   App ID: $ALGOLIA_APP_ID"
echo "   Index Name: $ALGOLIA_INDEX_NAME"

# Only this output enters agent context:
echo "✓ Search configured for Docusaurus site '$DOC_NAME' with Algolia DocSearch."