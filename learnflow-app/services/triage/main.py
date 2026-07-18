# Triage Agent Service - Routes queries to specialist agents
# LearnFlow AI Tutoring Platform

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
import uuid

from shared.base import (
    create_app, settings, logger, cache_get, cache_set,
    publish_event, get_current_user, get_optional_user,
    HealthResponse, PaginationParams, PaginatedResponse
)

# Update service name for this microservice
settings.service_name = "triage-agent"

app = create_app("triage-agent", "Triage Agent - Query Router")


# ============================================
# Models
# ============================================

class QueryType(str, Enum):
    EXPLAIN = "explain"
    DEBUG = "debug"
    CODE_REVIEW = "code_review"
    EXERCISE = "exercise"
    PROGRESS = "progress"
    GENERAL = "general"


class TriageRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=5000, description="Student's query")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")
    student_id: Optional[str] = None
    session_id: Optional[str] = None


class TriageResponse(BaseModel):
    query_type: QueryType
    confidence: float = Field(ge=0.0, le=1.0)
    routed_to: str
    reasoning: str
    suggested_prompt: Optional[str] = None
    metadata: Dict[str, Any] = {}


class TriageHistoryItem(BaseModel):
    id: str
    query: str
    query_type: QueryType
    confidence: float
    routed_to: str
    created_at: str


# ============================================
# Triage Logic
# ============================================

class TriageEngine:
    """Intelligent query routing engine"""
    
    # Keywords and patterns for each agent type
    KEYWORDS = {
        QueryType.EXPLAIN: [
            "explain", "how does", "what is", "define", "meaning", "concept",
            "understand", "learn about", "teach me", "tutorial", "introduction",
            "basics", "fundamentals", "overview", "summary"
        ],
        QueryType.DEBUG: [
            "error", "bug", "not working", "broken", "crash", "exception",
            "traceback", "fails", "failing", "doesn't work", "not working",
            "wrong output", "unexpected", "issue", "problem", "stuck"
        ],
        QueryType.CODE_REVIEW: [
            "review", "improve", "optimize", "refactor", "better", "clean",
            "best practice", "style", "pep8", "lint", "readable", "efficient",
            "performance", "security", "vulnerability"
        ],
        QueryType.EXERCISE: [
            "exercise", "practice", "challenge", "problem", "task", "homework",
            "assignment", "quiz", "test", "solve", "complete", "submit"
        ],
        QueryType.PROGRESS: [
            "progress", "mastery", "score", "level", "achievement", "badge",
            "streak", "rank", "percentage", "completed", "finished"
        ]
    }
    
    # Confidence thresholds
    MIN_CONFIDENCE = 0.3
    HIGH_CONFIDENCE = 0.7
    
    def __init__(self):
        self.query_cache = {}
    
    def classify(self, query: str, context: Dict = None) -> Dict[str, Any]:
        """Classify query and determine best agent"""
        query_lower = query.lower()
        scores = {}
        
        # Score each query type based on keyword matches
        for qtype, keywords in self.KEYWORDS.items():
            score = 0
            matches = []
            for keyword in keywords:
                if keyword in query_lower:
                    score += 1
                    matches.append(keyword)
            
            # Normalize by number of keywords
            normalized = score / len(keywords) if keywords else 0
            if matches:
                scores[qtype] = {
                    "score": normalized,
                    "matches": matches,
                    "raw_score": score
                }
        
        # Determine best match
        if not scores:
            return {
                "query_type": QueryType.GENERAL,
                "confidence": 0.5,
                "routed_to": "triage-agent",
                "reasoning": "No specific keywords matched, defaulting to general handler",
                "metadata": {"scores": {}}
            }
        
        best_type = max(scores, key=lambda k: scores[k]["score"])
        best_score = scores[best_type]["score"]
        matches = scores[best_type]["matches"]
        
        # Map query type to agent service name
        agent_map = {
            QueryType.EXPLAIN: "concepts-agent",
            QueryType.DEBUG: "debug-agent",
            QueryType.CODE_REVIEW: "code-review-agent",
            QueryType.EXERCISE: "exercise-agent",
            QueryType.PROGRESS: "progress-agent",
            QueryType.GENERAL: "triage-agent"
        }
        
        confidence = min(best_score * 2, 1.0)  # Scale up
        
        # Determine reasoning
        if confidence >= 0.7:
            reasoning = f"High confidence match for {best_type.value} based on keywords: {', '.join(matches[:3])}"
        elif confidence >= 0.4:
            reasoning = f"Moderate confidence for {best_type.value} based on keywords: {', '.join(matches[:3])}"
        else:
            reasoning = f"Low confidence, weakly matches {best_type.value} (keywords: {', '.join(matches[:2])})"
        
        return {
            "query_type": best_type,
            "confidence": round(confidence, 2),
            "routed_to": agent_map.get(best_type, "triage-agent"),
            "reasoning": reasoning,
            "metadata": {
                "scores": {k.value: v["score"] for k, v in scores.items()},
                "matched_keywords": matches,
                "all_scores": {k.value: v["score"] for k, v in scores.items()}
            }
        }
    
    async def route_query(self, request: Dict) -> Dict[str, Any]:
        """Route query to appropriate agent via Dapr"""
        from shared.base import dapr_client
        
        query = request.get("query", "")
        context = request.get("context", {})
        student_id = request.get("student_id")
        
        # Classify
        result = self.classify(request.get("query", ""), context)
        
        # Add metadata
        result["request_id"] = str(uuid.uuid4())
        result["student_id"] = student_id
        
        # Cache result
        cache_key = f"triage:{hash(request.get('query', ''))}"
        await cache_set(f"triage:{hash(request.get('query', ''))}", result, 300)
        
        return result


triage_engine = TriageEngine()


# ============================================
# API Endpoints
# ============================================

@app.post("/triage", response_model=TriageResponse)
async def triage_query(
    request: TriageRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Route a student query to the appropriate specialist agent"""
    
    student_id = current_user.get("sub") or request.student_id
    context = request.context or {}
    context["student_id"] = student_id
    
    # Check cache
    cache_key = f"triage:{hash(request.query)}"
    cached = await cache_get(f"triage:{hash(request.query)}")
    if cached:
        logger.info(f"Cache hit for triage query")
        return TriageResponse(**cached)
    
    # Classify query
    result = triage_engine.classify(request.query, {"student_id": student_id, **context})
    
    # Prepare response
    response = TriageResponse(
        query_type=result["query_type"],
        confidence=result["confidence"],
        routed_to=result["routed_to"],
        reasoning=result["reasoning"],
        metadata=result["metadata"]
    )
    
    # Cache result
    cache_key = f"triage:{hash(request.query)}"
    await cache_set(f"triage:{hash(request.query)}", response.model_dump(), 300)
    
    # Publish event for analytics
    background_tasks.add_task(
        publish_event,
        "triage.events",
        "query_routed",
        {
            "student_id": student_id,
            "query": request.query[:100],
            "query_type": result["query_type"].value,
            "confidence": result["confidence"],
            "routed_to": result["routed_to"]
        }
    )
    
    logger.info(f"Triage: '{request.query[:50]}...' -> {result['routed_to']} ({result['confidence']:.2f})")
    
    return response


@app.post("/triage/route")
async def route_and_forward(
    request: TriageRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Triage and forward query to appropriate agent via Dapr service invocation"""
    from shared.base import dapr_client
    
    student_id = current_user.get("sub") or request.student_id
    context = request.context or {}
    context["student_id"] = context.get("student_id") or student_id
    
    # Classify
    result = triage_engine.classify(request.query, {"student_id": student_id, **context})
    
    # Forward to appropriate agent
    agent = result["routed_to"]
    try:
        # Invoke the target agent service via Dapr
        agent_response = await dapr_client.invoke_service(
            app_id=result["routed_to"],
            method="process",
            data={
                "query": request.query,
                "context": context,
                "triage_result": {
                    "query_type": result["query_type"].value,
                    "confidence": result["confidence"],
                    "reasoning": result["reasoning"]
                }
            }
        )
        
        return {
            "triage": {
                "query_type": result["query_type"],
                "confidence": result["confidence"],
                "routed_to": result["routed_to"],
                "reasoning": result["reasoning"]
            },
            "agent_response": agent_response
        }
    except Exception as e:
        logger.error(f"Failed to invoke agent {result['routed_to']}: {e}")
        raise HTTPException(status_code=502, detail=f"Failed to invoke {result['routed_to']}")


@app.get("/triage/history", response_model=PaginatedResponse)
async def get_triage_history(
    params: PaginationParams = Depends(),
    current_user: dict = Depends(get_current_user)
):
    """Get triage history for current user"""
    # This would query from a history table in production
    # For now return mock data
    return PaginatedResponse(
        items=[],
        total=0,
        page=params.page,
        size=params.size,
        pages=0
    )


@app.get("/triage/stats")
async def get_triage_stats(current_user: dict = Depends(get_current_user)):
    """Get triage statistics"""
    return {
        "total_queries": 0,
        "by_type": {
            "explain": 0,
            "debug": 0,
            "code_review": 0,
            "exercise": 0,
            "progress": 0,
            "general": 0
        },
        "avg_confidence": 0.0
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="healthy",
        service="triage-agent",
        checks={
            "database": True,
            "redis": True,
            "dapr": True
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)