#!/usr/bin/env bash
# ai-exercise-engineer: generate-exercise.sh
# Generates a dynamic AI-powered programming exercise using the LLM service.
# Usage: generate-exercise.sh <topic> [difficulty]

TOPIC="${1:?Usage: generate-exercise.sh <topic> [difficulty]}"
DIFFICULTY="${2:-beginner}"

RESPONSE=$(curl -s --max-time 60 \
  -X POST http://localhost:8010/chat \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"openai/gpt-4o-mini\",
    \"messages\": [
      {\"role\": \"system\", \"content\": \"You are an expert programming exercise designer. Generate a JSON exercise for topic '$TOPIC' at '$DIFFICULTY' level. Include: id (uuid), title, description, difficulty, type (function_implementation), topic, starter_code (with pass/placeholder), solution_code, test_cases (array with input dict, expected_output, description, hidden: false), hints (array of 2-3 strings), estimated_minutes (number). Use real Python code. The test input keys must match variable names used in the student's code.\"},
      {\"role\": \"user\", \"content\": \"Create a $DIFFICULTY Python exercise about $TOPIC.\"}
    ],
    \"temperature\": 0.7,
    \"max_tokens\": 2000,
    \"response_format\": {\"type\": \"json_object\"}
  }")

echo "=========================================="
echo "  AI-GENERATED EXERCISE: $TOPIC"
echo "  Level: $DIFFICULTY"
echo "=========================================="
echo ""

echo "$RESPONSE" > /tmp/ai_exercise.json
python3 -c "
import json
with open('/tmp/ai_exercise.json') as f:
    raw = json.load(f)
content = raw.get('content', '')
try:
    ex = json.loads(content)
except json.JSONDecodeError:
    print(content)
    exit()

print(f'Title: {ex.get(\"title\", \"\")}')
print(f'Description: {ex.get(\"description\", \"\")}')
print(f'Difficulty: {ex.get(\"difficulty\", \"\")}')
print(f'Estimated time: {ex.get(\"estimated_minutes\", \"?\")} min')
print()
print('--- Starter Code ---')
print(ex.get('starter_code', ''))
print()
print('--- Hints ---')
for i, h in enumerate(ex.get('hints', []), 1):
    print(f'  {i}. {h}')
print()
print('--- Test Cases ---')
for i, tc in enumerate(ex.get('test_cases', []), 1):
    inp = tc.get('input', {})
    exp = tc.get('expected_output', '')
    desc = tc.get('description', '')
    print(f'  Test {i}: {desc}')
    print(f'    Input: {inp}')
    print(f'    Expected: {repr(exp)}')
"
