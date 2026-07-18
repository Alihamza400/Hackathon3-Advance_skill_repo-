# Code Review Agent Service - Analyzes code for correctness, style, efficiency
# LearnFlow AI Tutoring Platform

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Body
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from enum import Enum
import os
import uuid
import ast
import math
import re

from shared.base import (
    create_app, settings, logger, cache_get, cache_set,
    publish_event, get_current_user, get_optional_user,
    dapr_client, publish_event, HealthResponse
)

settings.service_name = "code-review-agent"

app = create_app("code-review-agent", "Code Review Agent - Code Analysis")


# ============================================
# Models
# ============================================

class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class IssueCategory(str, Enum):
    SYNTAX = "syntax"
    STYLE = "style"
    PERFORMANCE = "performance"
    SECURITY = "security"
    BEST_PRACTICE = "best_practice"
    BUG_RISK = "bug_risk"
    MAINTAINABILITY = "maintainability"


class ReviewIssue(BaseModel):
    line: int
    column: Optional[int] = None
    severity: Severity
    category: IssueCategory
    message: str
    suggestion: Optional[str] = None
    code_snippet: Optional[str] = None
    rule_id: Optional[str] = None


class CodeMetrics(BaseModel):
    lines_of_code: int
    cyclomatic_complexity: int
    cognitive_complexity: int
    maintainability_index: float
    halstead_volume: float
    halstead_difficulty: float
    halstead_effort: float
    lines_of_comments: int
    comment_ratio: float


class ReviewRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=50000, description="Code to review")
    language: Literal["python"] = "python"
    context: Optional[str] = None
    student_id: Optional[str] = None
    exercise_id: Optional[str] = None
    check_style: bool = True
    check_security: bool = True
    check_performance: bool = True
    check_best_practices: bool = True


class ReviewIssueDetail(BaseModel):
    line: int
    column: Optional[int] = None
    severity: Severity
    category: IssueCategory
    message: str
    suggestion: Optional[str] = None
    code_snippet: Optional[str] = None
    rule_id: Optional[str] = None


class ReviewSummary(BaseModel):
    total_issues: int
    by_severity: Dict[str, int]
    by_category: Dict[str, int]
    overall_score: float = Field(ge=0.0, le=100.0)
    metrics: CodeMetrics


class ReviewResponse(BaseModel):
    summary: ReviewSummary
    issues: List[ReviewIssueDetail]
    suggestions: List[str] = []
    passes: bool


# ============================================
# Code Analysis Engine
# ============================================

class CodeReviewEngine:
    """Advanced code analysis engine for Python code review"""
    
    def __init__(self):
        self.rules = self._load_rules()
    
    def _load_rules(self) -> List[Dict]:
        """Load linting rules"""
        return [
            # Security rules
            {
                "id": "SEC001",
                "pattern": r"eval\s*\(",
                "message": "Use of eval() is dangerous - can execute arbitrary code",
                "severity": Severity.CRITICAL,
                "category": IssueCategory.SECURITY,
                "suggestion": "Use ast.literal_eval() for safe evaluation or avoid dynamic code execution"
            },
            {
                "id": "SEC002",
                "pattern": r"exec\s*\(",
                "message": "Use of exec() is dangerous - can execute arbitrary code",
                "severity": Severity.CRITICAL,
                "category": IssueCategory.SECURITY,
                "suggestion": "Avoid dynamic code execution; use safer alternatives"
            },
            {
                "id": "SEC003",
                "pattern": r"__import__\s*\(",
                "message": "Dynamic import via __import__ can be a security risk",
                "severity": Severity.WARNING,
                "category": IssueCategory.SECURITY,
                "suggestion": "Use importlib.import_module() for dynamic imports"
            },
            {
                "id": "SEC004",
                "pattern": r"pickle\.loads?\s*\(",
                "message": "pickle can execute arbitrary code during deserialization",
                "severity": Severity.WARNING,
                "category": IssueCategory.SECURITY,
                "suggestion": "Use json or yaml for serialization; if pickle is required, validate source"
            },
            {
                "id": "SEC005",
                "pattern": r"subprocess\.(call|run|Popen)\s*\(",
                "message": "Subprocess calls can be a security risk if input is not sanitized",
                "severity": Severity.WARNING,
                "category": IssueCategory.SECURITY,
                "suggestion": "Validate and sanitize all inputs; use shell=False"
            },
            
            # Style rules (PEP 8)
            {
                "id": "STYLE001",
                "pattern": r"^[ \t]*[^#\s].{80,}",
                "message": "Line exceeds 79 characters (PEP 8)",
                "severity": Severity.WARNING,
                "category": IssueCategory.STYLE,
                "suggestion": "Break long lines using parentheses, backslashes, or split into multiple lines"
            },
            {
                "id": "STYLE002",
                "pattern": r"^\s*[^#].*[ \t]+$",
                "message": "Trailing whitespace",
                "severity": Severity.INFO,
                "category": IssueCategory.STYLE,
                "suggestion": "Remove trailing whitespace"
            },
            {
                "id": "STYLE003",
                "pattern": r"^[^#]*\b(def|class)\s+\w+[^:]*:\s*$",
                "message": "Missing docstring for public function/class",
                "severity": Severity.WARNING,
                "category": IssueCategory.BEST_PRACTICE,
                "suggestion": "Add docstring describing purpose, args, returns, and exceptions"
            },
            
            # Performance rules
            {
                "id": "PERF001",
                "pattern": r"\.append\s*\(.*\)\s*in\s+for\s+.*:",
                "message": "List comprehension would be more efficient than append in loop",
                "severity": Severity.WARNING,
                "category": IssueCategory.PERFORMANCE,
                "suggestion": "Use list comprehension: [expr for item in iterable]"
            },
            {
                "id": "PERF002",
                "pattern": r"for\s+\w+\s+in\s+range\s*\(\s*len\s*\(",
                "message": "Iterating over range(len()) - iterate directly over the sequence",
                "severity": Severity.WARNING,
                "category": IssueCategory.PERFORMANCE,
                "suggestion": "Use 'for item in sequence:' instead of 'for i in range(len(sequence)):'"
            },
            {
                "id": "PERF003",
                "pattern": r"\+=\s*[\"'].*[\"]",
                "message": "String concatenation in loop - use list and join",
                "severity": Severity.WARNING,
                "category": IssueCategory.PERFORMANCE,
                "suggestion": "Build list of strings and use ''.join(list) at the end"
            },
            {
                "id": "PERF004",
                "pattern": r"set\(\)",
                "message": "Creating empty set with set() - use set literal {} for non-empty",
                "severity": Severity.INFO,
                "category": IssueCategory.PERFORMANCE,
                "suggestion": "Use set() for empty set, but {} for non-empty"
            },
            
            # Bug risk rules
            {
                "id": "BUG001",
                "pattern": r"==\s*None|!=\s*None",
                "message": "Use 'is None' or 'is not None' instead of ==/!=",
                "severity": Severity.WARNING,
                "category": IssueCategory.BUG_RISK,
                "suggestion": "Use 'x is None' or 'x is not None' for None comparisons"
            },
            {
                "id": "BUG002",
                "pattern": r"\[\s*\d+\s*\]\s*$",
                "message": "Direct index access without bounds checking",
                "severity": Severity.WARNING,
                "category": IssueCategory.BUG_RISK,
                "suggestion": "Use try/except or check length before indexing"
            },
            {
                "id": "BUG003",
                "pattern": r"except\s*:",
                "message": "Bare except clause catches all exceptions including SystemExit",
                "severity": Severity.WARNING,
                "category": IssueCategory.BUG_RISK,
                "suggestion": "Use 'except Exception:' or specify exception types"
            },
            {
                "id": "BUG004",
                "pattern": r"\[\s*\]",
                "message": "Mutable default argument - use None as default instead",
                "severity": Severity.ERROR,
                "category": IssueCategory.BUG_RISK,
                "suggestion": "Use 'def func(arg=None): if arg is None: arg = []'"
            },
            
            # Best practices
            {
                "id": "BP001",
                "pattern": r"print\s*\(",
                "message": "Print statement found - use logging instead",
                "severity": Severity.INFO,
                "category": IssueCategory.BEST_PRACTICE,
                "suggestion": "Use logging module for production code"
            },
            {
                "id": "BP002",
                "pattern": r"def\s+\w+\s*\([^)]*\)\s*:\s*(?:pass|return\s+None)",
                "message": "Empty function body - consider implementing or removing",
                "severity": Severity.INFO,
                "category": IssueCategory.MAINTAINABILITY,
                "suggestion": "Implement the function or remove if not needed"
            },
            {
                "id": "BP003",
                "pattern": r"class\s+\w+\s*\(.*\):\s*(?:pass|$)",
                "message": "Empty class definition",
                "severity": Severity.INFO,
                "category": IssueCategory.MAINTAINABILITY,
                "suggestion": "Implement the class or remove if not needed"
            }
        ]
    
    def analyze(self, code: str, options: Dict[str, bool]) -> Dict[str, Any]:
        """Perform comprehensive code review"""
        issues = []
        lines = code.split('\n')
        
        # Parse AST for deeper analysis
        ast_issues = self._analyze_ast(code)
        issues.extend(ast_issues)
        
        # Pattern-based rules
        if options.get("check_style", True) or options.get("check_security", True) or \
           options.get("check_performance", True) or options.get("check_best_practices", True):
            pattern_issues = self._check_patterns(code, lines, options)
            issues.extend(pattern_issues)
        
        # Calculate metrics
        metrics = self._calculate_metrics(code)
        
        # Calculate scores
        summary = self._calculate_summary(issues, metrics)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(issues, metrics)
        
        return {
            "summary": summary,
            "issues": issues,
            "suggestions": suggestions,
            "passes": summary.overall_score >= 70.0
        }
    
    def _analyze_ast(self, code: str) -> List[Dict]:
        """Analyze AST for structural issues"""
        issues = []
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                # Check for mutable default arguments
                if isinstance(node, ast.FunctionDef):
                    for default in node.args.defaults:
                        if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                            issues.append({
                                "line": node.lineno,
                                "column": node.col_offset,
                                "severity": Severity.ERROR,
                                "category": IssueCategory.BUG_RISK,
                                "message": f"Mutable default argument '{default}' in function '{node.name}'",
                                "suggestion": "Use None as default and create mutable object inside function",
                                "code_snippet": f"def {node.name}(...):",
                                "rule_id": "AST001"
                            })
                
                # Check for bare except
                if isinstance(node, ast.ExceptHandler) and node.type is None:
                    issues.append({
                        "line": node.lineno,
                        "column": node.col_offset,
                        "severity": Severity.WARNING,
                        "category": IssueCategory.BUG_RISK,
                        "message": "Bare except clause catches all exceptions",
                        "suggestion": "Use 'except Exception:' or specify exception types",
                        "code_snippet": "except:",
                        "rule_id": "AST002"
                    })
                
                # Check for unused variables
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id.startswith('_'):
                            # Check if used later
                            pass  # Would need more complex analysis
        
        except SyntaxError as e:
            issues.append({
                "line": e.lineno or 0,
                "column": e.offset or 0,
                "severity": Severity.CRITICAL,
                "category": IssueCategory.SYNTAX,
                "message": f"Syntax error: {e.msg}",
                "suggestion": "Fix syntax error before review",
                "code_snippet": "",
                "rule_id": "AST_SYNTAX"
            })
        except Exception:
            pass
        
        return issues
    
    def _check_patterns(self, code: str, lines: List[str], options: Dict[str, bool]) -> List[Dict]:
        issues = []
        
        for rule in self.rules:
            category = rule["category"]
            
            # Skip if category not enabled
            if category == IssueCategory.STYLE and not options.get("check_style", True):
                continue
            if category == IssueCategory.SECURITY and not options.get("check_security", True):
                continue
            if category == IssueCategory.PERFORMANCE and not options.get("check_performance", True):
                continue
            if category in [IssueCategory.BEST_PRACTICE, IssueCategory.MAINTAINABILITY] and not options.get("check_best_practices", True):
                continue
            
            pattern = rule["pattern"]
            for i, line in enumerate(lines):
                if re.search(pattern, line):
                    issues.append({
                        "line": i + 1,
                        "column": None,
                        "severity": rule["severity"],
                        "category": category,
                        "message": rule["message"],
                        "suggestion": rule["suggestion"],
                        "code_snippet": line.strip()[:100],
                        "rule_id": rule["id"]
                    })
        
        return issues
    
    def _calculate_metrics(self, code: str) -> CodeMetrics:
        lines = code.split('\n')
        lines_of_code = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
        lines_of_comments = len([l for l in lines if l.strip().startswith('#')])
        
        # Simplified cyclomatic complexity
        complexity_keywords = ['if', 'elif', 'while', 'for', 'except', 'and', 'or', '?']
        cyclomatic = 1 + sum(code.count(kw) for kw in complexity_keywords)
        
        # Cognitive complexity (simplified)
        cognitive = cyclomatic + code.count('else') + code.count('elif')
        
        # Maintainability index (simplified)
        mi = max(0, 171 - 5.2 * cyclomatic - 0.23 * lines_of_code - 16.2 * math.log(lines_of_code + 1))
        mi = max(0, min(100, mi))
        
        # Halstead metrics (simplified)
        operators = len(re.findall(r'[\+\-\*/%=<>!&|^~]=?|//|\*\*|<<|>>', code))
        operands = len(re.findall(r'\b\w+\b', code))
        halstead_volume = (operators + operands) * math.log2(operators + operands + 1) if operators + operands > 0 else 0
        halstead_difficulty = (operators / 2) * (operands / max(1, len(set(re.findall(r'\b\w+\b', code)))))
        halstead_effort = halstead_difficulty * halstead_volume
        
        comment_ratio = lines_of_comments / max(1, lines_of_code) if lines_of_code > 0 else 0
        
        return CodeMetrics(
            lines_of_code=lines_of_code,
            cyclomatic_complexity=cyclomatic,
            cognitive_complexity=cognitive,
            maintainability_index=round(mi, 1),
            halstead_volume=round(halstead_volume, 1),
            halstead_difficulty=round(halstead_difficulty, 1),
            halstead_effort=round(halstead_effort, 1),
            lines_of_comments=lines_of_comments,
            comment_ratio=round(comment_ratio, 2)
        )
    
    def _calculate_summary(self, issues: List[Dict], metrics: CodeMetrics) -> ReviewSummary:
        by_severity = {}
        by_category = {}
        
        for issue in issues:
            sev = issue["severity"].value if isinstance(issue["severity"], Severity) else issue["severity"]
            cat = issue["category"].value if isinstance(issue["category"], IssueCategory) else issue["category"]
            by_severity[sev] = by_severity.get(sev, 0) + 1
            by_category[cat] = by_category.get(cat, 0) + 1
        
        # Calculate overall score
        penalty = (
            by_severity.get(Severity.CRITICAL.value, 0) * 20 +
            by_severity.get(Severity.ERROR.value, 0) * 10 +
            by_severity.get(Severity.WARNING.value, 0) * 3 +
            by_severity.get(Severity.INFO.value, 0) * 1
        )
        score = max(0, 100 - penalty)
        
        # Bonus for good metrics
        if metrics.maintainability_index > 80:
            score += 5
        if metrics.comment_ratio > 0.2:
            score += 5
        
        return ReviewSummary(
            total_issues=len(issues),
            by_severity=by_severity,
            by_category=by_category,
            overall_score=min(100, round(score, 1)),
            metrics=metrics
        )
    
    def _generate_suggestions(self, issues: List[Dict], metrics: CodeMetrics) -> List[str]:
        suggestions = []
        
        if any(i["category"] == IssueCategory.SECURITY for i in issues):
            suggestions.append("Address security issues immediately - they pose real risks")
        
        if any(i["category"] == IssueCategory.PERFORMANCE for i in issues):
            suggestions.append("Consider performance optimizations for better efficiency")
        
        if metrics.cyclomatic_complexity > 10:
            suggestions.append("High cyclomatic complexity - consider breaking into smaller functions")
        
        if metrics.maintainability_index < 50:
            suggestions.append("Low maintainability - refactor for readability")
        
        if metrics.comment_ratio < 0.1:
            suggestions.append("Add more comments and docstrings for better maintainability")
        
        if not suggestions:
            suggestions.append("Code looks good! Consider adding more tests.")
        
        return suggestions


review_engine = CodeReviewEngine()


# ============================================
# API Endpoints
# ============================================

@app.post("/review", response_model=ReviewResponse)
async def review_code(
    request: ReviewRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Review code for quality, security, performance, and best practices"""
    
    student_id = current_user.get("sub") or request.student_id
    
    # Check cache
    cache_key = f"review:{hash(request.code)}"
    cached = await cache_get(f"review:{hash(request.code)}")
    if cached:
        logger.info(f"Cache hit for code review")
        return ReviewResponse(**cached)
    
    # Perform review
    options = {
        "check_style": request.check_style,
        "check_security": request.check_security,
        "check_performance": request.check_performance,
        "check_best_practices": request.check_best_practices
    }
    
    result = review_engine.analyze(request.code, options)
    
    response = ReviewResponse(
        summary=result["summary"],
        issues=[ReviewIssueDetail(**issue) for issue in result["issues"]],
        suggestions=result["suggestions"],
        passes=result["passes"]
    )
    
    # Cache result
    cache_key = f"review:{hash(request.code)}"
    await cache_set(f"review:{hash(request.code)}", response.model_dump(), 3600)
    
    # Publish event
    background_tasks.add_task(
        publish_event,
        "code.reviewed",
        "code_reviewed",
        {
            "student_id": current_user.get("sub"),
            "exercise_id": request.exercise_id,
            "total_issues": result["summary"].total_issues,
            "overall_score": result["summary"].overall_score,
            "passes": result["passes"]
        }
    )
    
    return response


@app.post("/review/syntax")
async def check_syntax(
    code: str = Body(..., embed=True),
    current_user: dict = Depends(get_current_user)
):
    """Quick syntax check only"""
    try:
        ast.parse(code)
        return {"valid": True, "errors": []}
    except SyntaxError as e:
        return {"valid": False, "errors": [{"line": e.lineno, "message": e.msg}]}


@app.post("/review/metrics")
async def get_metrics(
    code: str = Body(..., embed=True),
    current_user: dict = Depends(get_current_user)
):
    """Get code metrics without full review"""
    result = review_engine.analyze(code, {"check_style": False, "check_security": False, 
                                          "check_performance": False, "check_best_practices": False})
    return {"metrics": result["summary"].metrics.model_dump()}


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="healthy",
        service="code-review-agent",
        checks={"database": True, "redis": True, "dapr": True}
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)