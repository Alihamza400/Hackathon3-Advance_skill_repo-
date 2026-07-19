#!/usr/bin/env bash
# concept-reasoner: reason-concept.sh
# Deep LLM-powered concept explanation with reasoning.
# Usage: reason-concept.sh <concept> [difficulty]

CONCEPT="${1:?Usage: reason-concept.sh <concept> [difficulty]}"
LEVEL="${2:-beginner}"

echo "=========================================="
echo "  $CONCEPT ($LEVEL)"
echo "=========================================="
echo ""

RESPONSE=$(curl -s --max-time 30 \
  -X POST http://localhost:8010/explain \
  -H "Content-Type: application/json" \
  -d "{\"concept\":\"$CONCEPT\",\"level\":\"$LEVEL\"}")

echo "$RESPONSE" > /tmp/concept_reason.json

python3 -c "
import json
with open('/tmp/concept_reason.json') as f:
    d = json.load(f)

print(d.get('definition', ''))
print()
print('--- Key Points ---')
for k in d.get('key_points', []):
    print(f'  \u2022 {k}')
print()
print('--- Analogies ---')
for a in d.get('analogies', []):
    print(f'  \u2022 {a}')
if not d.get('analogies'):
    print('  (none provided)')
print()
print('--- Code Examples ---')
for ex in d.get('code_examples', []):
    print(f'  Title: {ex.get(\"title\", \"\")}')
    print(f'  Explanation: {ex.get(\"explanation\", \"\")}')
    code = ex.get('code', '')
    for line in code.split(chr(10)):
        print(f'    {line}')
    print()
print('--- Common Mistakes ---')
for m in d.get('common_mistakes', []):
    print(f'  \u26a0 {m}')
print()
print('--- Related Concepts ---')
for r in d.get('related_concepts', []):
    print(f'  \u2192 {r}')
print()
print('==========================================')
print('  Ask follow-up: ask-followup.sh \"'\"$CONCEPT\"'\" \"your question\"')
print('==========================================')
" 2>&1
