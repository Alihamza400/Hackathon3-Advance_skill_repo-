import asyncio
import logging
import re
import asyncpg
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("db_server")

app = FastAPI(title="Database MCP Server", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "learnflow",
    "password": "learnflow",
    "database": "learnflow",
}


class QueryRequest(BaseModel):
    query: str


def validate_read_only(query: str) -> str:
    stripped = query.strip().rstrip(";").strip()
    if not re.match(r"^\s*SELECT\b", stripped, re.IGNORECASE):
        raise HTTPException(status_code=400, detail="Only SELECT queries are allowed")
    forbidden = re.findall(
        r"\b(INSERT|UPDATE|DELETE|DROP|TRUNCATE|ALTER|CREATE|REPLACE|EXEC|EXECUTE|MERGE|CALL)\b",
        query,
        re.IGNORECASE,
    )
    if forbidden:
        raise HTTPException(
            status_code=400,
            detail=f"Query contains forbidden statements: {', '.join(set(forbidden))}",
        )
    return stripped


async def get_pool():
    return await asyncpg.create_pool(**DB_CONFIG, min_size=1, max_size=5)


@app.on_event("startup")
async def startup():
    try:
        app.state.pool = await get_pool()
        logger.info("Connected to PostgreSQL")
    except Exception as e:
        logger.warning(f"Could not connect to PostgreSQL: {e}")
        app.state.pool = None


@app.on_event("shutdown")
async def shutdown():
    if hasattr(app.state, "pool") and app.state.pool:
        await app.state.pool.close()


@app.get("/health")
async def health():
    return {"status": "ok", "service": "db-mcp-server"}


@app.get("/mcp/db/tables")
async def list_tables():
    if not hasattr(app.state, "pool") or not app.state.pool:
        raise HTTPException(status_code=503, detail="Database not available")
    async with app.state.pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' ORDER BY table_name"
        )
    return {"tables": [r["table_name"] for r in rows]}


@app.get("/mcp/db/schema")
async def get_schema():
    if not hasattr(app.state, "pool") or not app.state.pool:
        raise HTTPException(status_code=503, detail="Database not available")
    async with app.state.pool.acquire() as conn:
        tables = await conn.fetch(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' ORDER BY table_name"
        )
        schema = {}
        for t in tables:
            name = t["table_name"]
            columns = await conn.fetch(
                "SELECT column_name, data_type, is_nullable "
                "FROM information_schema.columns "
                "WHERE table_schema = 'public' AND table_name = $1 "
                "ORDER BY ordinal_position",
                name,
            )
            schema[name] = [
                {
                    "name": c["column_name"],
                    "type": c["data_type"],
                    "nullable": c["is_nullable"] == "YES",
                }
                for c in columns
            ]
    return {"schema": schema}


@app.post("/mcp/db/query")
async def execute_query(req: QueryRequest):
    if not hasattr(app.state, "pool") or not app.state.pool:
        raise HTTPException(status_code=503, detail="Database not available")
    query = validate_read_only(req.query)
    async with app.state.pool.acquire() as conn:
        try:
            result = await asyncio.wait_for(conn.fetch(query), timeout=10.0)
        except asyncio.TimeoutError:
            raise HTTPException(status_code=408, detail="Query timed out after 10s")
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    return {
        "columns": list(result[0].keys()) if result else [],
        "rows": [dict(r) for r in result],
        "row_count": len(result),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8100)
