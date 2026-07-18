# LLM Agent Service - Dynamic AI responses via OpenRouter
# LearnFlow AI Tutoring Platform

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from openai import OpenAI, APIError
from datetime import datetime, timezone
import os
import json
import re

app = FastAPI(title="LLM Agent", version="1.0.0")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE = os.getenv("OPENROUTER_BASE", "https://openrouter.ai/api/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-4o-mini")
SITE_URL = os.getenv("SITE_URL", "https://learnflow.app")
SITE_NAME = os.getenv("SITE_NAME", "LearnFlow")

client = None
if OPENROUTER_API_KEY:
    client = OpenAI(
        base_url=OPENROUTER_BASE,
        api_key=OPENROUTER_API_KEY,
        default_headers={
            "HTTP-Referer": SITE_URL,
            "X-Title": SITE_NAME,
        }
    )

class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class Message(BaseModel):
    role: Role
    content: str

class ChatRequest(BaseModel):
    messages: List[Message] = Field(..., min_length=1)
    model: Optional[str] = None
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=2000, ge=1, le=16000)
    stream: Optional[bool] = False

class ChatResponse(BaseModel):
    content: str
    model: str
    usage: Optional[Dict[str, int]] = None

class ExplainRequest(BaseModel):
    concept: str = Field(..., min_length=1, max_length=200)
    level: Optional[str] = "beginner"
    context: Optional[str] = None

class ExplainResponse(BaseModel):
    concept: str
    definition: str
    explanation: str
    key_points: List[str]
    code_examples: List[Dict[str, str]]
    common_mistakes: List[str]
    related_concepts: List[str]
    model: str

class DebugRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=10000)
    error_message: Optional[str] = None

class DebugResponse(BaseModel):
    error_type: str
    explanation: str
    fixed_code: Optional[str] = None
    hints: List[str]
    model: str

@app.get("/health")
async def health():
    return {
        "status": "healthy" if client else "degraded",
        "service": "llm-agent",
        "llm_connected": client is not None,
        "model": LLM_MODEL,
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not client:
        raise HTTPException(status_code=503, detail="LLM not configured — set OPENROUTER_API_KEY")
    
    try:
        kwargs = {
            "model": request.model or LLM_MODEL,
            "messages": [{"role": m.role.value, "content": m.content} for m in request.messages],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }
        
        resp = client.chat.completions.create(**kwargs)
        
        return ChatResponse(
            content=resp.choices[0].message.content or "",
            model=resp.model,
            usage={"prompt_tokens": resp.usage.prompt_tokens, "completion_tokens": resp.usage.completion_tokens} if resp.usage else None,
        )
    except APIError as e:
        raise HTTPException(status_code=502, detail=f"LLM API error: {e.message}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/explain")
async def explain(request: ExplainRequest):
    if not client:
        raise HTTPException(status_code=503, detail="LLM not configured")

    prompt = f"""Explain the Python concept "{request.concept}" at {request.level} level.

Return your response as valid JSON with these exact keys:
- concept: the concept name
- definition: one-sentence definition
- explanation: 2-3 paragraph explanation with analogies
- key_points: array of 3-5 key takeaways
- code_examples: array of {{"title": string, "code": string, "explanation": string}} with 2-3 examples
- common_mistakes: array of 2-3 common mistakes
- related_concepts: array of 2-3 related Python concepts

Only return the JSON object, no markdown. Make it beginner-friendly."""

    try:
        resp = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are a Python tutor. Return only valid JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        
        content = resp.choices[0].message.content or "{}"
        data = json.loads(content)
        
        return ExplainResponse(
            concept=data.get("concept", request.concept),
            definition=data.get("definition", ""),
            explanation=data.get("explanation", ""),
            key_points=data.get("key_points", []),
            code_examples=data.get("code_examples", []),
            common_mistakes=data.get("common_mistakes", []),
            related_concepts=data.get("related_concepts", []),
            model=resp.model,
        )
    except (json.JSONDecodeError, APIError) as e:
        raise HTTPException(status_code=502, detail=f"LLM error: {e}")

@app.post("/debug")
async def debug_code(request: DebugRequest):
    if not client:
        raise HTTPException(status_code=503, detail="LLM not configured")

    prompt = f"""Debug this Python code:
```python
{request.code}
```
{f"Error: {request.error_message}" if request.error_message else "Find and fix any issues."}

Return JSON with:
- error_type: type of error (syntax_error, runtime_error, logic_error, etc.)
- explanation: what went wrong and why
- fixed_code: corrected version of the code
- hints: array of 2-3 debugging hints"""

    try:
        resp = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are a Python debugging expert. Return only valid JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        
        data = json.loads(resp.choices[0].message.content or "{}")
        return DebugResponse(
            error_type=data.get("error_type", "unknown"),
            explanation=data.get("explanation", ""),
            fixed_code=data.get("fixed_code"),
            hints=data.get("hints", []),
            model=resp.model,
        )
    except (json.JSONDecodeError, APIError) as e:
        raise HTTPException(status_code=502, detail=f"LLM error: {e}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8010"))
    uvicorn.run(app, host="0.0.0.0", port=port)
