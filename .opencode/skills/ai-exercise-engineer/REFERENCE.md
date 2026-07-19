# AI Exercise Engineer Skill

Generates dynamic programming exercises using the LLM service instead of static templates. Covers any topic not in the hardcoded exercise templates.

## Script: `scripts/generate-exercise.sh`

```bash
bash .opencode/skills/ai-exercise-engineer/scripts/generate-exercise.sh "closures" "intermediate"
```

Outputs a complete exercise with:
- Title and description
- Starter code
- Solution code
- 3-5 test cases with inputs and expected outputs
- 2-3 hints
- Estimated difficulty and time

## How it works

The script calls `POST /chat` on the LLM service with `response_format={"type": "json_object"}` and a structured system prompt that instructs the LLM to generate a valid exercise JSON. The LLM produces exercises dynamically for ANY topic — no hardcoded templates needed.

## Usage Examples

```bash
# Beginner exercise
bash generate-exercise.sh "variables" "beginner"

# Advanced algorithm
bash generate-exercise.sh "dynamic programming" "advanced"

# Niche topic
bash generate-exercise.sh "monads" "intermediate"
```

## Integration

Generated exercises can be fed to the exercise service's grading system via the existing `/exercises/submit` endpoint, or used standalone for practice.
