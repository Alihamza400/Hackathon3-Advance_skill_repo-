# Concept-Speaker Skill

Generates spoken-word explanations of programming concepts using an LLM, formatted for natural text-to-speech delivery.

## Endpoint

```
POST http://localhost:8010/explain
{
  "concept": "polymorphism",
  "level": "beginner"
}
```

Response includes `definition`, `explanation`, `analogies`, `code_examples`, and `key_points` — all formatted for speech.

## Speech Formatting Rules

- Sentences under 25 words
- Natural conversational transitions ("Now, let's talk about...", "Think of it this way...")
- Bullet points converted to spoken lists ("First... Second... Finally...")
- Code examples described verbally, not read character-by-character
- Technical terms followed by brief pronunciation guides in parentheses

## Script: `scripts/speak-concept.sh`

Usage:
```bash
bash .opencode/skills/concept-speaker/scripts/speak-concept.sh "polymorphism" "beginner"
```

Outputs speech-formatted text to stdout. Pipe to any TTS engine:
```bash
bash scripts/speak-concept.sh "async/await" "intermediate" | say   # macOS
bash scripts/speak-concept.sh "closures" "advanced" | festival --tts  # Linux
```
