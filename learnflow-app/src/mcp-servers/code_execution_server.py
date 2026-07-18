import logging
import os
import resource
import subprocess
import tempfile
import time
import traceback
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("code_execution_server")

app = FastAPI(title="Code Execution MCP Server", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

EXECUTION_TIMEOUT = 5
MEMORY_LIMIT = 50 * 1024 * 1024


class CodeRequest(BaseModel):
    code: str
    stdin: str = ""


class AnalysisRequest(BaseModel):
    code: str = ""
    error: str


def set_limits():
    resource.setrlimit(resource.RLIMIT_AS, (MEMORY_LIMIT, MEMORY_LIMIT))
    resource.setrlimit(resource.RLIMIT_RSS, (MEMORY_LIMIT, MEMORY_LIMIT))


@app.get("/health")
async def health():
    return {"status": "ok", "service": "code-execution-mcp-server"}


@app.post("/mcp/execute")
async def execute_code(req: CodeRequest):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(req.code)
        fpath = f.name

    start = time.time()
    try:
        proc = subprocess.Popen(
            ["python3", fpath],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=set_limits,
            text=True,
        )
        try:
            stdout, stderr = proc.communicate(input=req.stdin, timeout=EXECUTION_TIMEOUT)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()
            elapsed = round(time.time() - start, 3)
            os.unlink(fpath)
            return {
                "stdout": stdout,
                "stderr": "Execution timed out after 5 seconds",
                "exit_code": -1,
                "execution_time": elapsed,
                "timed_out": True,
            }
        elapsed = round(time.time() - start, 3)
        return {
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": proc.returncode,
            "execution_time": elapsed,
            "timed_out": False,
        }
    except Exception as e:
        elapsed = round(time.time() - start, 3)
        os.unlink(fpath)
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "execution_time": elapsed},
        )
    finally:
        if os.path.exists(fpath):
            os.unlink(fpath)


@app.post("/mcp/analyze")
async def analyze_error(req: AnalysisRequest):
    hints = []
    error_lower = req.error.lower()

    if "syntaxerror" in error_lower:
        hints.append("Check for missing colons, parentheses, or indentation issues.")
    if "indentationerror" in error_lower or "unexpected indent" in error_lower:
        hints.append("Ensure consistent indentation (use spaces, not tabs).")
    if "importerror" in error_lower or "modulenotfounderror" in error_lower:
        hints.append("The module may not be installed or the name may be misspelled.")
    if "attributeerror" in error_lower:
        hints.append("The object does not have that attribute. Check the attribute name.")
    if "typeerror" in error_lower:
        hints.append("Check the types of arguments being passed to the function.")
    if "valueerror" in error_lower:
        hints.append("The value is not valid for the expected type. Check your input.")
    if "keyerror" in error_lower:
        hints.append("The dictionary key does not exist. Verify the key name.")
    if "indexerror" in error_lower:
        hints.append("The list index is out of range. Check your loop bounds.")
    if "zerodivisionerror" in error_lower:
        hints.append("Cannot divide by zero. Check your denominator.")
    if "filenotfounderror" in error_lower:
        hints.append("The file path is incorrect or the file does not exist.")
    if "nameerror" in error_lower:
        hints.append("A variable or function name is not defined. Check for typos.")
    if "recursionerror" in error_lower:
        hints.append("Too many recursive calls. Check your base case.")

    if not hints:
        hints.append("Review the error message and check for common mistakes.")

    return {
        "error": req.error,
        "hints": hints,
        "suggestion": hints[0] if hints else "No specific hints available.",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8101)
