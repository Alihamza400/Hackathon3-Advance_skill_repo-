"""
LearnFlow Microservices - Shared Base Module
Common utilities, models, and base classes for all microservices
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, EmailStr
from pydantic_settings import BaseSettings
import httpx
import redis.asyncio as redis
import asyncpg
import jwt
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# ============================================
# Configuration
# ============================================

class Settings(BaseSettings):
    service_name: str = os.getenv("SERVICE_NAME", "learnflow-service")
    log_level: str = os.getenv("LOG_LEVEL", "info")
    
    # Database
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    postgres_db: str = os.getenv("POSTGRES_DB", "learnflow")
    postgres_user: str = os.getenv("POSTGRES_USER", "learnflow")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "")
    
    # Redis
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_password: str = os.getenv("REDIS_PASSWORD", "")
    redis_ssl: bool = os.getenv("REDIS_SSL", "true").lower() == "true"
    
    # Kafka
    kafka_brokers: str = os.getenv("KAFKA_BROKERS", "localhost:9092")
    
    # Dapr
    dapr_http_port: int = int(os.getenv("DAPR_HTTP_PORT", "3500"))
    dapr_grpc_port: int = int(os.getenv("DAPR_GRPC_PORT", "50001"))
    
    # JWT
    jwt_secret: str = os.getenv("JWT_SECRET", "learnflow-jwt-secret-key-change-in-production")
    jwt_algorithm: str = "HS256"
    jwt_expiry_minutes: int = 60 * 24  # 24 hours
    
    # Service
    service_port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

# ============================================
# Logging Setup
# ============================================

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(settings.service_name)

# ============================================
# Prometheus Metrics
# ============================================

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["service", "method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["service", "method", "endpoint"]
)

ACTIVE_REQUESTS = Gauge(
    "http_active_requests",
    "Active HTTP requests",
    ["service"]
)

# ============================================
# Database Connection Pool
# ============================================

_pool: Optional[asyncpg.Pool] = None
_redis_client: Optional[redis.Redis] = None


async def get_db_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        try:
            _pool = await asyncio.wait_for(
                asyncpg.create_pool(
                    host=settings.postgres_host,
                    port=settings.postgres_port,
                    database=settings.postgres_db,
                    user=settings.postgres_user,
                    password=settings.postgres_password,
                    min_size=1,
                    max_size=5,
                    command_timeout=5,
                ),
                timeout=5
            )
        except asyncio.TimeoutError:
            logger.warning("DB connection timed out, running without database")
            _pool = None
    return _pool


async def close_db_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


async def get_redis() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        try:
            _redis_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                password=settings.redis_password or None,
                ssl=settings.redis_ssl,
                decode_responses=True,
                max_connections=5,
                socket_connect_timeout=2,
                socket_timeout=2,
            )
            await asyncio.wait_for(_redis_client.ping(), timeout=3)
        except (asyncio.TimeoutError, redis.ConnectionError, OSError) as e:
            logger.warning(f"Redis connection failed: {e}, running without cache")
            _redis_client = None
    return _redis_client


async def close_redis():
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None


# ============================================
# Dapr Client
# ============================================

class DaprClient:
    """Dapr HTTP client for service invocation, state, pub/sub"""
    
    def __init__(self):
        self.base_url = f"http://localhost:{settings.dapr_http_port}"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def invoke_service(self, app_id: str, method: str, data: dict = None, 
                            http_method: str = "POST") -> dict:
        """Invoke another Dapr service"""
        url = f"{self.base_url}/v1.0/invoke/{app_id}/method/{method}"
        response = await self.client.request(http_method, url, json=data)
        response.raise_for_status()
        return response.json()
    
    async def save_state(self, store: str, key: str, value: dict) -> None:
        """Save state to Dapr state store"""
        url = f"{self.base_url}/v1.0/state/{store}"
        data = [{"key": key, "value": value}]
        response = await self.client.post(url, json=data)
        response.raise_for_status()
    
    async def get_state(self, store: str, key: str) -> Optional[dict]:
        """Get state from Dapr state store"""
        url = f"{self.base_url}/v1.0/state/{store}/{key}"
        response = await self.client.get(url)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        data = response.json()
        return data[0]["value"] if data else None
    
    async def delete_state(self, store: str, key: str) -> None:
        """Delete state from Dapr state store"""
        url = f"{self.base_url}/v1.0/state/{store}/{key}"
        response = await self.client.delete(url)
        response.raise_for_status()
    
    async def publish_event(self, pubsub: str, topic: str, data: dict) -> None:
        """Publish event to Dapr pub/sub"""
        url = f"{self.base_url}/v1.0/publish/{pubsub}/{topic}"
        response = await self.client.post(url, json=data)
        response.raise_for_status()
    
    async def get_secret(self, store: str, key: str) -> str:
        """Get secret from Dapr secret store"""
        url = f"{self.base_url}/v1.0/secrets/{store}/{key}"
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()[key]
    
    async def close(self):
        await self.client.aclose()


dapr_client = DaprClient()


# ============================================
# Pydantic Models
# ============================================

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    checks: Dict[str, bool] = {}


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int


# ============================================
# Authentication
# ============================================

def create_access_token(data: dict, expires_delta: Optional[int] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + datetime.timedelta(
        minutes=expires_delta or settings.jwt_expiry_minutes
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.split(" ")[1]
    return decode_token(token)


async def get_optional_user(authorization: Optional[str] = Header(None)) -> Optional[dict]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    try:
        token = authorization.split(" ")[1]
        return decode_token(token)
    except:
        return None


# ============================================
# Middleware
# ============================================

async def metrics_middleware(request: Request, call_next):
    ACTIVE_REQUESTS.labels(service=settings.service_name).inc()
    start_time = datetime.now()
    
    try:
        response = await call_next(request)
        duration = (datetime.now() - start_time).total_seconds()
        
        REQUEST_COUNT.labels(
            service=settings.service_name,
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        REQUEST_LATENCY.labels(
            service=settings.service_name,
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)
        
        return response
    finally:
        ACTIVE_REQUESTS.labels(service=settings.service_name).dec()


async def logging_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id", "unknown")
    logger.info(f"[{request_id}] {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"[{request_id}] {response.status_code}")
    return response


# ============================================
# Lifespan
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.service_name}")
    try:
        await asyncio.wait_for(get_db_pool(), timeout=3)
    except Exception as e:
        logger.warning(f"DB unavailable: {e}")
    try:
        await asyncio.wait_for(get_redis(), timeout=3)
    except Exception as e:
        logger.warning(f"Redis unavailable: {e}")
    logger.info(f"{settings.service_name} started")

    yield

    logger.info(f"Shutting down {settings.service_name}")
    await close_db_pool()
    await close_redis()
    await dapr_client.close()
    logger.info(f"{settings.service_name} stopped")


def create_app(service_name: str, title: str = None) -> FastAPI:
    """Create a FastAPI app with standard middleware and endpoints"""
    
    settings.service_name = service_name
    
    app = FastAPI(
        title=title or service_name,
        version="1.0.0",
        lifespan=lifespan,
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://app.learnflow.com", "https://docs.learnflow.com"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Middleware
    app.middleware("http")(metrics_middleware)
    app.middleware("http")(logging_middleware)
    
    # Health endpoints
    @app.get("/health", response_model=HealthResponse)
    async def health():
        checks = {
            "database": False,
            "redis": False,
            "dapr": False,
        }
        
        # Check database
        try:
            pool = await get_db_pool()
            async with pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            checks["database"] = True
        except:
            pass
        
        # Check Redis
        try:
            redis_client = await get_redis()
            await redis_client.ping()
            checks["redis"] = True
        except:
            pass
        
        # Check Dapr
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"http://localhost:{settings.dapr_http_port}/v1.0/healthz", timeout=2)
                checks["dapr"] = resp.status_code == 200
        except:
            pass
        
        all_healthy = all(checks.values())
        status = "healthy" if all_healthy else "degraded"
        
        return HealthResponse(
            status=status,
            service=settings.service_name,
            checks=checks
        )
    
    @app.get("/health/ready")
    async def readiness():
        return {"ready": True}
    
    @app.get("/metrics")
    async def metrics():
        return generate_latest()
    
    return app


# ============================================
# Database Helpers
# ============================================

async def fetch_one(query: str, *args) -> Optional[dict]:
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, *args)
        return dict(row) if row else None


async def fetch_all(query: str, *args) -> List[dict]:
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, *args)
        return [dict(row) for row in rows]


async def execute(query: str, *args) -> str:
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        return await conn.execute(query, *args)


async def fetch_val(query: str, *args):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        return await conn.fetchval(query, *args)


# ============================================
# Redis Helpers
# ============================================

async def cache_get(key: str) -> Optional[Any]:
    client = await get_redis()
    if client is None:
        return None
    try:
        data = await client.get(key)
        return json.loads(data) if data else None
    except Exception:
        return None


async def cache_set(key: str, value: Any, ttl: int = 3600) -> None:
    client = await get_redis()
    if client is None:
        return
    try:
        await client.setex(key, ttl, json.dumps(value, default=str))
    except Exception:
        pass


async def cache_delete(key: str) -> None:
    client = await get_redis()
    if client is None:
        return
    try:
        await client.delete(key)
    except Exception:
        pass


async def cache_delete_pattern(pattern: str) -> None:
    client = await get_redis()
    if client is None:
        return
    try:
        keys = await client.keys(pattern)
        if keys:
            await client.delete(*keys)
    except Exception:
        pass


# ============================================
# Event Publishing
# ============================================

async def publish_event(topic: str, event_type: str, payload: dict, 
                       correlation_id: str = None) -> None:
    """Publish event to Kafka via Dapr pub/sub"""
    event = {
        "type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "correlation_id": correlation_id,
        "source": settings.service_name,
        "payload": payload,
    }
    await dapr_client.publish_event("pubsub", topic, event)


# ============================================
# Error Handlers
# ============================================

async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.__class__.__name__,
            message=exc.detail,
            request_id=request.headers.get("x-request-id")
        ).model_dump()
    )


async def validation_exception_handler(request: Request, exc):
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error="ValidationError",
            message="Invalid request data",
            details={"errors": exc.errors()},
            request_id=request.headers.get("x-request-id")
        ).model_dump()
    )


async def general_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="InternalServerError",
            message="An unexpected error occurred",
            request_id=request.headers.get("x-request-id")
        ).model_dump()
    )


def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)


# ============================================
# Pagination Helper
# ============================================

def paginate(query: str, params: PaginationParams, *args) -> dict:
    """Helper to paginate SQL queries"""
    offset = (params.page - 1) * params.size
    total_query = f"SELECT COUNT(*) FROM ({query}) AS count_query"
    total = fetch_val(total_query, *args)
    
    data_query = f"{query} LIMIT {params.size} OFFSET {offset}"
    items = fetch_all(data_query, *args)
    
    return {
        "items": items,
        "total": total,
        "page": params.page,
        "size": params.size,
        "pages": (total + params.size - 1) // params.size
    }