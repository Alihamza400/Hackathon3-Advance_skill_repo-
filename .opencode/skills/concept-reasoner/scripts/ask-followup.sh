#!/usr/bin/env bash
# concept-reasoner: ask-followup.sh
# Ask a follow-up question about a previously explained concept.
# Usage: ask-followup.sh <concept> <question>

CONCEPT="${1:?Usage: ask-followup.sh <concept> <question>}"
QUESTION="${2:?Usage: ask-followup.sh <concept> <question>}"

echo "Q: $QUESTION"
echo ""

curl -s --max-time 30 \
  -X POST http://localhost:8010/chat \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"openai/gpt-4o-mini\",
    \"messages\": [
      {\"role\": \"system\", \"content\": \"You are a patient programming tutor explaining $CONCEPT. Use simple language, analogies, and short code examples. Answer conversationally.\"},
      {\"role\": \"user\", \"content\": \"$QUESTION\"}
    ],
    \"temperature\": 0.5,
    \"max_tokens\": 1000
  }" | python3 -c "
import sys,json
d=json.load(sys.stdin)
print(d.get('content',''))
" 2>/dev/null
