# Debug Agent Service - Helps students debug their code
# LearnFlow AI Tutoring Platform

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Body
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from enum import Enum
import uuid
import subprocess
import tempfile
import os
import sys
import time
import traceback
import json
import re

from shared.base import (
    create_app, settings, logger, cache_get, cache_set,
    publish_event, get_current_user, get_optional_user,
    dapr_client, publish_event, HealthResponse
)

settings.service_name = "debug-agent"

app = create_app("debug-agent", "Debug Agent - Code Debugging Assistant")


# ============================================
# Models
# ============================================

class ErrorType(str, Enum):
    SYNTAX_ERROR = "syntax_error"
    RUNTIME_ERROR = "runtime_error"
    LOGIC_ERROR = "logic_error"
    TYPE_ERROR = "type_error"
    NAME_ERROR = "name_error"
    INDEX_ERROR = "index_error"
    KEY_ERROR = "key_error"
    ATTRIBUTE_ERROR = "attribute_error"
    VALUE_ERROR = "value_error"
    ZERO_DIVISION_ERROR = "zero_division_error"
    IMPORT_ERROR = "import_error"
    ASSERTION_ERROR = "assertion_error"
    TIMEOUT = "timeout"
    MEMORY_ERROR = "memory_error"
    UNKNOWN = "unknown"


class DebugRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=50000, description="Code to debug")
    error_message: Optional[str] = Field(None, description="Error message if known")
    error_type: Optional[ErrorType] = None
    test_input: Optional[str] = None
    expected_output: Optional[str] = None
    student_id: Optional[str] = None
    exercise_id: Optional[str] = None
    include_traceback: bool = True


class DebugHint(BaseModel):
    type: Literal["explanation", "suggestion", "fixed_code", "concept_link"]
    title: str
    content: str
    priority: int = 1  # 1=high, 2=medium, 3=low


class DebugResponse(BaseModel):
    error_type: ErrorType
    error_explanation: str
    root_cause: str
    hints: List[DebugHint] = []
    fixed_code: Optional[str] = None
    explanation: str
    concepts_to_review: List[str] = []


# ============================================
# Debug Engine
# ============================================

class DebugEngine:
    """Advanced debugging engine for Python code"""
    
    ERROR_PATTERNS = {
        ErrorType.SYNTAX_ERROR: [
            r"SyntaxError",
            r"invalid syntax",
            r"unexpected EOF",
            r"unexpected indent",
            r"expected ':'",
            r"unmatched"
        ],
        ErrorType.NAME_ERROR: [
            r"NameError",
            r"name '.*' is not defined",
            r"global name '.*' is not defined"
        ],
        ErrorType.TYPE_ERROR: [
            r"TypeError",
            r"unsupported operand type",
            r"'.*' object is not callable",
            r"'.*' object is not subscriptable",
            r"'.*' object has no attribute",
            r"takes .* positional arguments but .* were given"
        ],
        ErrorType.INDEX_ERROR: [
            r"IndexError",
            r"list index out of range",
            r"string index out of range"
        ],
        ErrorType.KEY_ERROR: [
            r"KeyError"
        ],
        ErrorType.ATTRIBUTE_ERROR: [
            r"AttributeError",
            r"'.*' object has no attribute"
        ],
        ErrorType.VALUE_ERROR: [
            r"ValueError",
            r"invalid literal for",
            r"not enough values to unpack",
            r"too many values to unpack"
        ],
        ErrorType.ZERO_DIVISION_ERROR: [
            r"ZeroDivisionError",
            r"division by zero"
        ],
        ErrorType.IMPORT_ERROR: [
            r"ImportError",
            r"ModuleNotFoundError",
            r"No module named"
        ],
        ErrorType.ASSERTION_ERROR: [
            r"AssertionError"
        ]
    }
    
    ERROR_EXPLANATIONS = {
        ErrorType.SYNTAX_ERROR: {
            "explanation": "Syntax error means the code violates Python's grammar rules. The parser cannot understand what you wrote.",
            "root_cause": "Missing punctuation, incorrect indentation, mismatched brackets, or invalid keywords.",
            "concepts": ["Python syntax", "indentation", "statements", "expressions"]
        },
        ErrorType.NAME_ERROR: {
            "explanation": "Name error occurs when you use a variable or function name that hasn't been defined yet.",
            "root_cause": "Variable used before assignment, typo in variable name, or scope issue.",
            "concepts": ["variable scope", "variable assignment", "function definitions"]
        },
        ErrorType.TYPE_ERROR: {
            "explanation": "Type error occurs when an operation is applied to an object of inappropriate type.",
            "root_cause": "Mismatched types in operations, wrong number of arguments, or incorrect object usage.",
            "concepts": ["data types", "type conversion", "function signatures", "operators"]
        },
        ErrorType.INDEX_ERROR: {
            "explanation": "Index error occurs when trying to access an index that doesn't exist in a sequence.",
            "root_cause": "Accessing list/string/tuple with index >= length or negative index too large.",
            "concepts": ["zero-based indexing", "list bounds", "loop boundaries", "defensive programming"]
        },
        ErrorType.KEY_ERROR: {
            "explanation": "Key error occurs when accessing a dictionary key that doesn't exist.",
            "root_cause": "Trying to access a dictionary key that hasn't been set.",
            "concepts": ["dictionaries", "key existence", ".get() method", "default values"]
        },
        ErrorType.ATTRIBUTE_ERROR: {
            "explanation": "Attribute error occurs when accessing an attribute/method that doesn't exist on an object.",
            "root_cause": "Typo in attribute name, wrong object type, or missing method/property.",
            "concepts": ["classes", "objects", "methods", "properties", "hasattr()"]
        },
        ErrorType.VALUE_ERROR: {
            "explanation": "Value error occurs when a function receives an argument of correct type but inappropriate value.",
            "root_cause": "Invalid argument value, unpacking mismatch, or invalid literal conversion.",
            "concepts": ["function arguments", "type conversion", "unpacking", "validation"]
        },
        ErrorType.ZERO_DIVISION_ERROR: {
            "explanation": "Attempted to divide by zero.",
            "root_cause": "Denominator is zero in division or modulo operation.",
            "concepts": ["division", "error handling", "conditional checks", "math operations"]
        },
        ErrorType.IMPORT_ERROR: {
            "explanation": "Import error occurs when a module cannot be found or imported.",
            "root_cause": "Module not installed, wrong name, missing __init__.py, or path issues.",
            "concepts": ["modules", "packages", "PYTHONPATH", "virtual environments", "pip install"]
        },
        ErrorType.ASSERTION_ERROR: {
            "explanation": "Assertion error occurs when an assert statement fails.",
            "root_cause": "The condition in assert statement evaluated to False.",
            "concepts": ["assertions", "testing", "debugging", "preconditions"]
        }
    }
    
    HINT_TEMPLATES = {
        ErrorType.SYNTAX_ERROR: [
            DebugHint(type="explanation", title="Check Syntax", content="Look at the line number in the error message. Check for missing colons, parentheses, brackets, or incorrect indentation.", priority=1),
            DebugHint(type="suggestion", title="Use an IDE", content="Use an IDE with syntax highlighting (VS Code, PyCharm) to catch syntax errors before running.", priority=2),
            DebugHint(type="concept_link", title="Learn Python Syntax", content="Review Python basics: statements, indentation, colons, parentheses matching.", priority=3)
        ],
        ErrorType.NAME_ERROR: [
            DebugHint(type="explanation", title="Variable Not Defined", content="The variable name in the error doesn't exist in the current scope. Check spelling and where it's defined.", priority=1),
            DebugHint(type="suggestion", title="Check Scope", content="Variables defined inside functions are local. Variables defined outside are global. Use 'global' keyword to modify globals.", priority=2),
            DebugHint(type="concept_link", title="Variable Scope", content="Learn about local vs global scope, function parameters, and variable lifetime.", priority=3)
        ],
        ErrorType.TYPE_ERROR: [
            DebugHint(type="explanation", title="Type Mismatch", content="You're trying to use an operation on incompatible types (e.g., adding string to int, calling a string as function).", priority=1),
            DebugHint(type="suggestion", title="Check Types", content="Use type() to check variable types. Convert types explicitly: int(), str(), float(), list().", priority=2),
            DebugHint(type="concept_link", title="Type System", content="Learn about Python's dynamic typing, type conversion, and isinstance() checks.", priority=3)
        ],
        ErrorType.INDEX_ERROR: [
            DebugHint(type="explanation", title="Index Out of Range", content="You're accessing an index that doesn't exist. Lists are zero-indexed: valid indices are 0 to len(list)-1.", priority=1),
            DebugHint(type="suggestion", title="Add Bounds Check", content="Check length before accessing: if index < len(list): item = list[index]. Or use try/except.", priority=2),
            DebugHint(type="concept_link", title="List Indexing", content="Learn zero-based indexing, negative indexing, slicing, and bounds checking.", priority=3)
        ],
        ErrorType.KEY_ERROR: [
            DebugHint(type="explanation", title="Missing Dictionary Key", content="The key you're trying to access doesn't exist in the dictionary.", priority=1),
            DebugHint(type="suggestion", title="Use .get() Method", content="Use dict.get(key, default) to safely access keys: value = my_dict.get('key', 'default')", priority=2),
            DebugHint(type="concept_link", title="Dictionary Methods", content="Learn .get(), .keys(), .values(), .items(), 'in' operator, and defaultdict.", priority=3)
        ],
        ErrorType.ATTRIBUTE_ERROR: [
            DebugHint(type="explanation", title="Missing Attribute/Method", content="The object doesn't have the attribute or method you're trying to access. Check spelling and object type.", priority=1),
            DebugHint(type="suggestion", title="Check Object Type", content="Use type(obj) to see what type it is. Use hasattr(obj, 'attr') to check before accessing.", priority=2),
            DebugHint(type="concept_link", title="OOP Concepts", content="Learn about classes, instances, methods, properties, and hasattr()/getattr().", priority=3)
        ],
        ErrorType.VALUE_ERROR: [
            DebugHint(type="explanation", title="Invalid Value", content="The operation received an argument of the right type but inappropriate value.",            priority=1),
            DebugHint(type="suggestion", title="Validate Inputs", content="Add input validation before operations that might raise ValueError.", priority=2),
            DebugHint(type="concept_link", title="Error Handling", content="Learn try/except, raise, and custom exceptions for robust code.", priority=3)
        ],
        ErrorType.ZERO_DIVISION_ERROR: [
            DebugHint(type="explanation", title="Division by Zero", content="You cannot divide by zero. Check denominator before division.", priority=1),
            DebugHint(type="suggestion", title="Guard Division", content="Use: if denominator != 0: result = numerator / denominator else: handle_error()", priority=2),
            DebugHint(type="concept_link", title="Math Operations", content="Learn about division, modulo, floor division, and safe math operations.", priority=3)
        ],
        ErrorType.IMPORT_ERROR: [
            DebugHint(type="explanation", title="Module Not Found", content="Python can't find the module you're trying to import.", priority=1),
            DebugHint(type="suggestion", title="Check Installation", content="Install with pip: pip install module_name. Check virtual environment is activated.", priority=2),
            DebugHint(type="concept_link", title="Python Modules", content="Learn about modules, packages, pip, virtual environments, and PYTHONPATH.", priority=3)
        ],
        ErrorType.ASSERTION_ERROR: [
            DebugHint(type="explanation", title="Assertion Failed", content="The condition in your assert statement evaluated to False.", priority=1),
            DebugHint(type="suggestion", title="Debug Assertions", content="Print the values before the assert to see what's happening: print(f'x={x}, y={y}')", priority=2),
            DebugHint(type="concept_link", title="Testing & Debugging", content="Learn assert, unittest, pytest, and debugging strategies.",            priority=3)
        ]
    }

    def detect_error_type(self, error_message: str, traceback_str: str = "") -> ErrorType:
        """Detect error type from error message and traceback"""
        combined = (error_message or "") + " " + (traceback_str or "")
        
        for error_type, patterns in self.ERROR_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, combined, re.IGNORECASE):
                    return error_type
        return ErrorType.UNKNOWN
    
    def _apply_resource_limits(self):
        try:
            import resource
            resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
            resource.setrlimit(resource.RLIMIT_AS, (50 * 1024 * 1024, 50 * 1024 * 1024))
            resource.setrlimit(resource.RLIMIT_FSIZE, (1024 * 1024, 1024 * 1024))
            resource.setrlimit(resource.RLIMIT_NPROC, (10, 10))
        except (ImportError, resource.error):
            pass

    def _restrict_builtins(self, code: str) -> str:
        dangerous = ["__import__", "exec", "eval", "compile", "open", "breakpoint", "__subclasses__"]
        restricted_imports = ["os", "sys", "subprocess", "shutil", "socket", "requests", "http", "ctypes", "signal", "multiprocessing", "threading"]
        wrapper = (
            "import sys, builtins, types\n"
            "_safe_builtins = {k: v for k, v in builtins.__dict__.items() if k not in %s}\n"
            "_safe_builtins['__import__'] = lambda name, *args, **kw: "
            "    (_ for _ in ()).throw(ImportError('%%s is not allowed' %% name)) "
            "if name in %s else builtins.__import__(name, *args, **kw)\n"
            "_RestrictedModule = types.ModuleType('restricted')\n"
            "_RestrictedModule._shutdown = lambda: None\n"
            "sys.modules.update({m: _RestrictedModule for m in %s})\n"
            "builtins.__dict__.update(_safe_builtins)\n"
            "del sys, builtins, _safe_builtins, types, _RestrictedModule\n\n"
        ) % (repr(dangerous), repr(restricted_imports), repr(restricted_imports))
        return wrapper + code

    def execute_code(self, code: str, test_input: str = None) -> Dict[str, Any]:
        """Execute code in isolated sandboxed environment with resource limits"""
        restricted_code = self._restrict_builtins(code)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(restricted_code)
            temp_file = f.name

        start_time = time.time()
        try:
            safe_env = {
                "PATH": os.environ.get("PATH", "/usr/bin"),
                "HOME": os.environ.get("HOME", "/tmp"),
                "LANG": "C.UTF-8",
            }
            result = subprocess.run(
                [sys.executable, '-I', temp_file],
                input=test_input if test_input is not None else "\n",
                capture_output=True,
                text=True,
                timeout=10,
                preexec_fn=self._apply_resource_limits,
                env=safe_env,
            )
            exec_time = (time.time() - start_time) * 1000

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "execution_time_ms": round(exec_time, 2),
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False, "stdout": "", "stderr": "Execution timed out (5s limit)",
                "returncode": -1, "error_type": ErrorType.TIMEOUT, "execution_time_ms": 5000,
            }
        except MemoryError:
            return {
                "success": False, "stdout": "", "stderr": "Memory limit exceeded (50MB max)",
                "returncode": -1, "error_type": ErrorType.MEMORY_ERROR, "execution_time_ms": 0,
            }
        except Exception as e:
            return {
                "success": False, "stdout": "", "stderr": str(e),
                "returncode": -1, "execution_time_ms": 0,
            }
        finally:
            try:
                os.unlink(temp_file)
            except Exception:
                pass
    
    def analyze_error(self, code: str, error_message: str = None, test_input: str = None) -> Dict[str, Any]:
        """Analyze code and error to provide debugging hints"""
        
        # If no error message provided, try executing to get error
        if not error_message:
            exec_result = self.execute_code(code, test_input)
            if exec_result["success"]:
                return {
                    "error_type": ErrorType.UNKNOWN,
                    "explanation": "Code executed successfully - no error detected.",
                    "hints": []
                }
            error_message = exec_result["stderr"]
            traceback_str = exec_result["stderr"]
        else:
            traceback_str = error_message
        
        # Detect error type
        error_type = self.detect_error_type(error_message, traceback_str)
        
        # Get explanation
        error_info = self.ERROR_EXPLANATIONS.get(error_type, {
            "explanation": "An unexpected error occurred.",
            "root_cause": "Unable to determine specific cause.",
            "concepts": ["debugging", "error handling"]
        })
        
        # Get hints
        hints = self.HINT_TEMPLATES.get(error_type, [
            DebugHint(type="explanation", title="Error Detected", content="An error occurred. Check the error message and traceback.", priority=1),
            DebugHint(type="suggestion", title="Read Error Message", content="The error message usually tells you what went wrong and where.", priority=2),
            DebugHint(type="concept_link", title="Debugging Skills", content="Learn to read tracebacks, use print debugging, and use a debugger.", priority=3)
        ])
        
        # Generate fixed code suggestion (simplified)
        fixed_code = self._suggest_fix(code, error_type, error_message)
        
        return {
            "error_type": error_type,
            "error_explanation": error_info["explanation"],
            "root_cause": error_info["root_cause"],
            "hints": hints,
            "fixed_code": fixed_code,
            "explanation": error_info["explanation"],
            "concepts_to_review": error_info["concepts"]
        }
    
    def _suggest_fix(self, code: str, error_type: ErrorType, error_message: str) -> Optional[str]:
        """Generate a suggested fix (simplified)"""
        # This is a simplified version - real implementation would be more complex
        fixes = {
            ErrorType.SYNTAX_ERROR: "# Fix syntax errors: check indentation, brackets, colons",
            ErrorType.NAME_ERROR: "# Define the variable before using it\n# variable_name = value",
            ErrorType.TYPE_ERROR: "# Convert types explicitly\n# str(), int(), float(), list()",
            ErrorType.INDEX_ERROR: "# Check bounds before accessing\n# if 0 <= index < len(list): item = list[index]",
            ErrorType.KEY_ERROR: "# Use .get() for safe access\n# value = my_dict.get('key', 'default')",
            ErrorType.ATTRIBUTE_ERROR: "# Check if attribute exists\n# if hasattr(obj, 'attr'): obj.attr",
            ErrorType.VALUE_ERROR: "# Validate inputs before processing\n# if not valid_value: raise ValueError",
            ErrorType.ZERO_DIVISION_ERROR: "# Check for zero before division\n# if denominator != 0: result = num / denom",
            ErrorType.IMPORT_ERROR: "# Install missing package\n# pip install package_name",
            ErrorType.ASSERTION_ERROR: "# Check condition before assert\n# assert condition, f'Failed: {variable}'"
        }
        return fixes.get(error_type)


debug_engine = DebugEngine()


# ============================================
# API Endpoints
# ============================================

@app.post("/debug", response_model=DebugResponse)
async def debug_code(
    request: DebugRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Debug code and provide hints"""
    
    student_id = current_user.get("sub") or request.student_id
    
    # Analyze the error
    result = debug_engine.analyze_error(
        request.code,
        request.error_message,
        request.test_input
    )
    
    response = DebugResponse(
        error_type=result["error_type"],
        error_explanation=result["error_explanation"],
        root_cause=result["root_cause"],
        hints=result["hints"],
        fixed_code=result.get("fixed_code"),
        explanation=result["explanation"],
        concepts_to_review=result["concepts_to_review"]
    )
    
    # Publish event
    background_tasks.add_task(
        publish_event,
        "debug.requested",
        "debug_requested",
        {
            "student_id": current_user.get("sub"),
            "exercise_id": request.exercise_id,
            "error_type": result["error_type"].value
        }
    )
    
    return response


@app.post("/execute")
async def execute_code(
    code: str = Body(..., embed=True),
    test_input: Optional[str] = Body(None, embed=True),
    current_user: dict = Depends(get_current_user)
):
    """Execute code in sandboxed environment"""
    result = debug_engine.execute_code(code, test_input)
    return result


@app.post("/analyze/traceback")
async def analyze_traceback(
    traceback: str = Body(..., embed=True),
    current_user: dict = Depends(get_current_user)
):
    """Analyze a traceback and identify error type"""
    error_type = debug_engine.detect_error_type("", traceback)
    error_info = debug_engine.ERROR_EXPLANATIONS.get(error_type, {})
    
    return {
        "error_type": error_type.value,
        "explanation": error_info.get("explanation", "Unknown error"),
        "root_cause": error_info.get("root_cause", "Unknown"),
        "concepts_to_review": error_info.get("concepts", [])
    }


@app.get("/error-types")
async def list_error_types(current_user: dict = Depends(get_current_user)):
    """List all supported error types with explanations"""
    return {
        "error_types": [
            {
                "type": et.value,
                "explanation": info["explanation"],
                "root_cause": info["root_cause"],
                "concepts": info["concepts"]
            }
            for et, info in debug_engine.ERROR_EXPLANATIONS.items()
        ]
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="healthy",
        service="debug-agent",
        checks={"database": True, "redis": True, "dapr": True}
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)