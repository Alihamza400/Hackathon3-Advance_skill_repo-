# Concept Reasoner Skill

Leverages the LLM service's `/explain` and `/chat` endpoints to deliver deep, reasoned concept explanations.

## Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `http://localhost:8010/explain` | POST | Structured explanation (definition, key_points, analogies, code_examples, common_mistakes) |
| `http://localhost:8010/chat` | POST | Follow-up Q&A, deep reasoning, code walkthroughs |

## Scripts

### `scripts/reason-concept.sh`

Primary script. Fetches a structured explanation and enriches it with Socratic questioning.

```bash
bash .opencode/skills/concept-reasoner/scripts/reason-concept.sh "recursion" "intermediate"
```

### `scripts/ask-followup.sh`

Asks a follow-up question to deepen understanding of a previously explained concept.

```bash
bash .opencode/skills/concept-reasoner/scripts/ask-followup.sh "recursion" "show me a real-world example"
```

## Output Format

The script outputs a structured explanation with these sections:
1. Definition (plain language)
2. Key Points (numbered, spoken-word friendly)
3. Analogies (relatable comparisons)
4. Code Examples (with line-by-line reasoning)
5. Common Mistakes (what to watch out for)
6. Related Concepts (what to learn next)
