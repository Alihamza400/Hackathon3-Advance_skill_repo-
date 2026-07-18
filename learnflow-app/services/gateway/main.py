# API Gateway Service - Routes requests to microservices
# LearnFlow AI Tutoring Platform

from fastapi import FastAPI, HTTPException, Request, Depends, Header, Body
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import httpx
import asyncio
import time
import logging
import os
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LearnFlow API Gateway",
    description="API Gateway routing requests to LearnFlow microservices",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.learnflow.com", "https://docs.learnflow.com", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service registry
SERVICES = {
    "triage": "http://triage-agent:8000",
    "concepts": "http://concepts-agent:8000",
    "code-review": "http://code-review-agent:8000",
    "debug": "http://debug-agent:8000",
    "exercise": "http://exercise-agent:8000",
    "progress": "http://progress-agent:8000",
    "auth": "http://auth-service:8000",
}

# Health checks
SERVICE_HEALTH = {}

# Rate limiting
RATE_LIMITS = {
    "default": {"requests": 100, "window": 60},
    "auth": {"requests": 20, "window": 60},
    "exercise_submit": {"requests": 30, "window": 60},
}

_request_counts = {}

# In-memory cache stubs (replace with Redis in production)
_cache: Dict[str, Any] = {}

async def cache_get(key: str):
    return _cache.get(key)

async def cache_set(key: str, value: Any, ttl: int = 60):
    _cache[key] = value

# Service client
class ServiceClient:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def request(
        self,
        service: str,
        method: str,
        path: str,
        headers: Dict = None,
        params: Dict = None,
        json: Dict = None,
        data: Any = None,
        timeout: float = 30.0
    ) -> httpx.Response:
        if service not in SERVICES:
            raise HTTPException(status_code=404, detail=f"Service '{service}' not found")
        
        url = f"{SERVICES[service]}{path}"
        request_headers = headers or {}
        
        # Add tracing headers
        request_headers["X-Gateway-Request-ID"] = str(uuid.uuid4())
        
        try:
            response = await self.client.request(
                method=method,
                url=url,
                headers=request_headers,
                params=params,
                json=json,
                data=data,
                timeout=timeout
            )
            return response
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail=f"Service '{service}' timeout")
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail=f"Service '{service}' unavailable")
        except Exception as e:
            logger.error(f"Gateway error calling {service}: {e}")
            raise HTTPException(status_code=502, detail=f"Gateway error: {str(e)}")
    
    async def close(self):
        await self.client.aclose()


gateway_client = ServiceClient()


# Rate limiting
async def check_rate_limit(
    request: Request,
    limit: int = 100,
    window: int = 60,
    key_prefix: str = "default"
):
    client_ip = request.client.host
    key = f"ratelimit:{key_prefix}:{client_ip}"
    
    current = await cache_get(key)
    if current and current >= limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    count = (current or 0) + 1
    await cache_set(key, count, window)


# Auth dependency
async def get_current_user(
    authorization: Optional[str] = Header(None),
    x_user_id: Optional[str] = Header(None)
) -> Dict[str, Any]:
    if x_user_id:
        # For development/testing - pass user ID via header
        return {"sub": x_user_id, "roles": ["student"]}
    
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        # In production, validate JWT with auth service
        # For now, return mock user
        return {"sub": "dev-user", "roles": ["student"]}
    
    # Allow unauthenticated for some endpoints
    return None


# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Skip rate limiting for health checks
    if request.url.path in ["/health", "/healthz", "/ready"]:
        return await call_next(request)
    
    # Determine rate limit based on path
    if request.url.path.startswith("/auth/"):
        limit, window = RATE_LIMITS["auth"]["requests"], RATE_LIMITS["auth"]["window"]
        prefix = "auth"
    elif request.url.path.startswith("/exercises/") and request.method == "POST":
        limit, window = RATE_LIMITS["exercise_submit"]["requests"], RATE_LIMITS["exercise_submit"]["window"]
        prefix = "exercise_submit"
    else:
        limit, window = RATE_LIMITS["default"]["requests"], RATE_LIMITS["default"]["window"]
        prefix = "default"
    
    await check_rate_limit(request, limit, window, prefix)
    
    return await call_next(request)


# Request logging middleware
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start_time = time.time()
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    
    logger.info(f"[{request_id}] {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    logger.info(f"[{request_id}] {response.status_code} - {duration:.3f}s")
    
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time"] = f"{duration:.3f}s"
    
    return response


# ============================================
# Health & Status Endpoints
# ============================================

@app.get("/health")
async def health():
    """Gateway health check"""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "version": "1.0.0",
        "services": SERVICE_HEALTH
    }


@app.get("/healthz")
async def healthz():
    """Kubernetes liveness probe"""
    return {"status": "ok"}


@app.get("/ready")
async def ready():
    """Kubernetes readiness probe"""
    # Check if critical services are reachable
    unhealthy = []
    for service in ["auth", "triage", "exercise"]:
        if SERVICE_HEALTH.get(service) == "unhealthy":
            unhealthy.append(service)
    
    if unhealthy:
        return {"status": "not_ready", "unhealthy_services": unhealthy}
    return {"status": "ready"}


@app.get("/services/status")
async def services_status():
    """Get status of all backend services"""
    status = {}
    async with httpx.AsyncClient(timeout=5.0) as client:
        for name, url in SERVICES.items():
            try:
                response = await client.get(f"{url}/health", timeout=3.0)
                if response.status_code == 200:
                    status[name] = {"status": "healthy", "details": response.json()}
                else:
                    status[name] = {"status": "degraded", "code": response.status_code}
            except Exception as e:
                status[name] = {"status": "unhealthy", "error": str(e)}
    
    SERVICE_HEALTH.update(status)
    return {"services": status}


# ============================================
# Authentication Routes (proxy to auth service)
# ============================================

@app.post("/auth/login")
async def login(
    request: Request,
    credentials: Dict[str, str]
):
    """Proxy login to auth service"""
    response = await gateway_client.request(
        "auth", "POST", "/auth/login",
        json=credentials
    )
    return response.json()


@app.post("/auth/register")
async def register(
    request: Request,
    user_data: Dict[str, Any]
):
    """Proxy registration to auth service"""
    response = await gateway_client.request(
        "auth", "POST", "/auth/register",
        json=user_data
    )
    return response.json()


@app.post("/auth/refresh")
async def refresh_token(
    request: Request,
    refresh_token: str = Body(..., embed=True)
):
    """Refresh access token"""
    response = await gateway_client.request(
        "auth", "POST", "/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    return response.json()


@app.post("/auth/logout")
async def logout(
    request: Request,
    refresh_token: str = Body(..., embed=True),
    current_user: dict = Depends(get_current_user)
):
    """Logout and invalidate refresh token"""
    response = await gateway_client.request(
        "auth", "POST", "/auth/logout",
        json={"refresh_token": refresh_token},
        headers={"Authorization": f"Bearer {request.headers.get('Authorization', '').replace('Bearer ', '')}"}
    )
    return response.json()


@app.get("/auth/me")
async def get_me(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Get current user profile"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Forward to auth service for full profile
    response = await gateway_client.request(
        "auth", "GET", "/auth/me",
        headers={"Authorization": request.headers.get("Authorization", "")}
    )
    return response.json()


# ============================================
# Triage Agent Routes
# ============================================

@app.post("/triage")
async def triage_query(
    request: Request,
    query_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Route query to triage agent"""
    response = await gateway_client.request(
        "triage", "POST", "/triage",
        json=query_data,
        headers={"Authorization": request.headers.get("Authorization", "")}
    )
    return response.json()


@app.post("/triage/route")
async def route_query(
    request: Request,
    query_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Route and forward query to appropriate agent"""
    response = await gateway_client.request(
        "triage", "POST", "/triage/route",
        json=query_data,
        headers={"Authorization": request.headers.get("Authorization", "")}
    )
    return response.json()


# ============================================
# Concepts Agent Routes
# ============================================

@app.post("/concepts/explain")
async def explain_concept(
    request: Request,
    explain_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Explain a concept"""
    response = await gateway_client.request(
        "concepts", "POST", "/explain",
        json=explain_data,
        headers={"Authorization": request.headers.get("Authorization", "")}
    )
    return response.json()


@app.get("/concepts/list")
async def list_concepts(
    request: Request,
    level: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """List available concepts"""
    params = {}
    if level:
        params["level"] = level
    
    response = await gateway_client.request(
        "concepts", "GET", "/concepts/list",
        params=params,
        headers={"Authorization": request.headers.get("Authorization", "")}
    )
    return response.json()


# ============================================
# Code Review Agent Routes
# ============================================

@app.post("/code-review/review")
async def review_code(
    request: Request,
    review_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Review code"""
    response = await gateway_client.request(
        "code-review", "POST", "/review",
        json=review_data,
        headers={"Authorization": request.headers.get("Authorization", "")}
    )
    return response.json()


@app.post("/code-review/syntax")
async def check_syntax(
    request: Request,
    code: str = Body(..., embed=True),
    current_user: dict = Depends(get_current_user)
):
    """Quick syntax check"""
    response = await gateway_client.request(
        "code-review", "POST", "/review/syntax",
        json={"code": code},
        headers={"Authorization": request.headers.get("Authorization", "")}
    )
    return response.json()


@app.post("/code-review/metrics")
async def get_metrics(
    request: Request,
    code: str = Body(..., embed=True),
    current_user: dict = Depends(get_current_user)
):
    """Get code metrics"""
    response = await gateway_client.request(
        "code-review", "POST", "/review/metrics",
        json={"code": code},
        headers={"Authorization": request.headers.get("Authorization", "")}
    )
    return response.json()


# ============================================
# Debug Agent Routes
# ============================================

@app.post("/debug")
async def debug_code(
    request: Request,
    debug_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Debug code"""
    response = await gateway_client.request(
        "debug", "POST", "/debug",
        json=debug_data,
        headers={"Authorization": request.headers.get("Authorization", "")}
    )
    return response.json()


@app.post("/debug/execute")
async def execute_code(
    request: Request,
    code: str = Body(..., embed=True),
    test_input: Optional[str] = Body(None, embed=True),
    current_user: dict = Depends(get_current_user)
):
    """Execute code in sandbox"""
    response = await gateway_client.request(
        "debug", "POST", "/execute",
        json={"code": code, "test_input": test_input},
        headers={"Authorization": request.headers.get("Authorization", "")}
    )
    return response.json()


@app.post("/debug/analyze")
async def analyze_traceback(
    request: Request,
    traceback: str = Body(..., embed=True),
    current_user: dict = Depends(get_current_user)
):
    """Analyze traceback"""
    response = await gateway_client.request(
        "debug", "POST", "/analyze/traceback",
        json={"traceback": traceback},
        headers={"Authorization": request.headers.get("Authorization", "")}
    )
    return response.json()


# ============================================
# Exercise Agent Routes
# ============================================

@app.post("/exercises/generate")
async def generate_exercises(
    request: Request,
    generate_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Generate exercises"""
    response = await gateway_client.request(
        "exercise", "POST", "/exercises/generate",
        json=generate_data,
        headers={"Authorization": request.headers.get("Authorization", "")}
    )
    return response.json()


@app.get("/exercises/{exercise_id}")
async def get_exercise(
    exercise_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Get exercise by ID"""
    response = await gateway_client.request(
        "exercise", "GET", f"/exercises/{exercise_id}",
        headers={"Authorization": request.headers.get("Authorization", "")}
    )
    return response.json()


@app.post("/exercises/submit")
async def submit_exercise(
    request: Request,
    submit_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Submit exercise solution"""
    response = await gateway_client.request(
        "exercise", "POST", "/exercises/submit",
        json=submit_data,
        headers={"Authorization": request.headers.get("Authorization", "")}
    )
    return response.json()


# ============================================
# Progress Agent Routes
# ============================================

@app.post("/progress/events")
async def record_progress_event(
    request: Request,
    event_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Record progress event"""
    response = await gateway_client.request(
        "progress", "POST", "/events",
        json=event_data,
        headers={"Authorization": request.headers.get("Authorization", "")}
    )
    return response.json()


@app.get("/progress/dashboard")
async def get_dashboard(
    current_user: dict = Depends(get_current_user)
):
    """Get student dashboard"""
    response = await gateway_client.request(
        "progress", "GET", "/progress/dashboard",
        headers={"Authorization": request.headers.get("Authorization", "")}
    )
    return response.json()


@app.get("/progress/streak")
async def get_streak(
    current_user: dict = Depends(get_current_user)
):
    """Get streak info"""
    response = await gateway_client.request(
        "progress", "GET", "/progress/streak",
        headers={"Authorization": request.headers.get("Authorization", "")}
    )
    return response.json()


# Teacher endpoints
@app.get("/teacher/dashboard")
async def teacher_dashboard(
    current_user: dict = Depends(get_current_user)
):
    """Get teacher dashboard"""
    # Check if user is teacher
    if "teacher" not in current_user.get("roles", []):
        raise HTTPException(status_code=403, detail="Teacher access required")
    
    response = await gateway_client.request(
        "progress", "GET", "/teacher/dashboard",
        headers={"Authorization": request.headers.get("Authorization", "")}
    )
    return response.json()


# ============================================
# Catch-all proxy for unmatched routes
# ============================================

@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_request(
    service: str,
    path: str,
    request: Request,
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Proxy requests to backend services"""
    if service not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Service '{service}' not found")
    
    # Prepare headers
    headers = dict(request.headers)
    if current_user:
        headers["X-User-ID"] = current_user.get("sub", "")
        headers["X-User-Roles"] = ",".join(current_user.get("roles", []))
    
    # Get query params
    params = dict(request.query_params)
    
    # Get body for non-GET requests
    body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        body = await request.body()
    
    response = await gateway_client.request(
        service,
        request.method,
        f"/{path}",
        headers=headers,
        params=params,
        data=body,
        timeout=60.0
    )
    
    # Return streaming response for large responses
    return StreamingResponse(
        response.aiter_bytes(),
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.headers.get("content-type")
    )


@app.on_event("shutdown")
async def shutdown():
    await gateway_client.close()


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)