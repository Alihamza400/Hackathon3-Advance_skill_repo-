#!/usr/bin/env bash
# concept-speaker: speak-concept.sh
# Fetches a concept explanation from the LLM service and formats it for TTS.
# Usage: bash speak-concept.sh <concept> [level]
#   concept  - required, the programming concept to explain
#   level    - optional, one of: beginner, intermediate, advanced (default: beginner)

CONCEPT="${1:?Usage: speak-concept.sh <concept> [level]}"
LEVEL="${2:-beginner}"

RESPONSE=$(curl -s --max-time 30 \
  -X POST http://localhost:8010/explain \
  -H "Content-Type: application/json" \
  -d "{\"concept\":\"$CONCEPT\",\"level\":\"$LEVEL\"}")

echo "Let me explain $CONCEPT."
echo ""

DEFINITION=$(echo "$RESPONSE" | python3 -c "import sys,json;print(json.load(sys.stdin).get('definition','')[:300])" 2>/dev/null)
if [ -n "$DEFINITION" ]; then
  echo "$DEFINITION"
  echo ""
fi

echo "Here is a simple analogy."
echo ""
ANALOGY=$(echo "$RESPONSE" | python3 -c "
import sys,json
d=json.load(sys.stdin)
for a in d.get('analogies',d.get('key_points',['Think of it like this'])):
    print(a)
    break
" 2>/dev/null)
echo "$ANALOGY"
echo ""

echo "To summarize the key points:"
echo ""
python3 -c "
import sys,json
d=json.load(sys.stdin)
points = d.get('key_points',d.get('explanation','').split('.')[:3])
for i, p in enumerate(points[:4], 1):
    text = str(p).strip().rstrip('.')
    if text:
        print(f'Number {i}: {text}.')
" 2>/dev/null <<< "$RESPONSE"
echo ""
echo "I hope this explanation of $CONCEPT was helpful."
