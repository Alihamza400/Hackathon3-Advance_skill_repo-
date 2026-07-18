# Exercise Agent Service - Generates and grades coding challenges
# LearnFlow AI Tutoring Platform

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from enum import Enum
import uuid
import json
import subprocess
import tempfile
import os
import sys
import textwrap

from shared.base import (
    create_app, settings, logger, cache_get, cache_set,
    publish_event, get_current_user, get_optional_user,
    dapr_client
)

settings.service_name = "exercise-agent"

app = create_app("exercise-agent", "Exercise Agent - Challenge Generator & Grader")


# ============================================
# Models
# ============================================

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class ExerciseType(str, Enum):
    CODE_COMPLETION = "code_completion"
    BUG_FIX = "bug_fix"
    FUNCTION_IMPLEMENTATION = "function_implementation"
    ALGORITHM = "algorithm"
    DEBUG = "debug"
    CODE_REVIEW = "code_review"


class TestCase(BaseModel):
    input: Dict[str, Any] = {}
    expected_output: Any
    description: Optional[str] = None
    hidden: bool = False


class Exercise(BaseModel):
    id: str
    title: str
    description: str
    difficulty: DifficultyLevel
    type: ExerciseType
    topic: str
    subtopic: Optional[str] = None
    starter_code: str
    solution_code: str
    test_cases: List[TestCase]
    hints: List[str] = []
    estimated_minutes: int
    points: int
    prerequisites: List[str] = []
    tags: List[str] = []


class ExerciseRequest(BaseModel):
    topic: str
    difficulty: DifficultyLevel = DifficultyLevel.BEGINNER
    type: Optional[ExerciseType] = None
    subtopic: Optional[str] = None
    count: int = 1
    student_id: Optional[str] = None


class GeneratedExercise(BaseModel):
    exercises: List[Exercise]


class SubmissionRequest(BaseModel):
    exercise_id: str
    code: str
    student_id: Optional[str] = None


class TestResult(BaseModel):
    test_case: TestCase
    passed: bool
    actual_output: Any
    error: Optional[str] = None
    execution_time_ms: int


class SubmissionResult(BaseModel):
    exercise_id: str
    passed: bool
    score: float = Field(ge=0.0, le=100.0)
    test_results: List[TestResult]
    feedback: str
    hints: List[str] = []
    concepts_to_review: List[str] = []
    execution_time_ms: int


# ============================================
# Exercise Generator
# ============================================

class ExerciseGenerator:
    """Generates coding exercises based on topic and difficulty"""
    
    EXERCISE_TEMPLATES = {
        "variable": {
            "beginner": [
                {
                    "title": "Store and Print a Variable",
                    "description": "Create a variable called `name` and assign it your name as a string. Then print it.",
                    "starter_code": "# Create a variable called name with your name\nname = \n\n# Print the variable\nprint(name)",
                    "solution_code": "name = \"Alice\"\nprint(name)",
                    "test_cases": [
                        {"input": {}, "expected_output": "Alice\n", "description": "Prints the name"},
                    ],
                    "hints": [
                        "Use quotes around text strings",
                        "The print() function outputs to screen"
                    ],
                    "estimated_minutes": 5,
                    "points": 10
                }
            ],
            "intermediate": [
                {
                    "title": "Swap Two Variables",
                    "description": "Swap the values of two variables without using a temporary variable.",
                    "starter_code": "a = 10\nb = 20\n# Swap a and b here\n\nprint(f\"a = {a}, b = {b}\")",
                    "solution_code": "a = 10\nb = 20\na, b = b, a\nprint(f\"a = {a}, b = {b}\")",
                    "test_cases": [
                        {"input": {}, "expected_output": "a = 20, b = 10\n"},
                    ],
                    "hints": ["Python supports tuple unpacking for swapping"],
                    "estimated_minutes": 10,
                    "points": 15
                }
            ]
        },
        "function": {
            "beginner": [
                {
                    "title": "Create a Greeting Function",
                    "description": "Write a function called `greet` that takes a name parameter and returns a greeting string.",
                    "starter_code": "def greet(name):\n    # Return greeting string\n    pass\n\n# Test your function\nprint(greet(\"Alice\"))",
                    "solution_code": "def greet(name):\n    return f\"Hello, {name}!\"\n\nprint(greet(\"Alice\"))",
                    "test_cases": [
                        {"input": {"name": "Alice"}, "expected_output": "Hello, Alice!\n"},
                        {"input": {"name": "Bob"}, "expected_output": "Hello, Bob!\n"},
                    ],
                    "hints": [
                        "Use f-strings for string formatting",
                        "The function should return, not print"
                    ],
                    "estimated_minutes": 10,
                    "points": 15
                }
            ],
            "intermediate": [
                {
                    "title": "Calculate Factorial",
                    "description": "Write a recursive function to calculate the factorial of a number.",
                    "starter_code": "def factorial(n):\n    # Implement recursive factorial\n    pass\n\n# Test\nprint(factorial(5))",
                    "solution_code": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)\n\nprint(factorial(5))",
                    "test_cases": [
                        {"input": {"n": 5}, "expected_output": "120\n"},
                        {"input": {"n": 0}, "expected_output": "1\n"},
                        {"input": {"n": 1}, "expected_output": "1\n"},
                    ],
                    "hints": [
                        "Base case: factorial(0) = 1 and factorial(1) = 1",
                        "Recursive case: n * factorial(n-1)"
                    ],
                    "estimated_minutes": 15,
                    "points": 25
                }
            ]
        },
        "loop": {
            "beginner": [
                {
                    "title": "Print Numbers 1 to N",
                    "description": "Write a loop that prints numbers from 1 to n (inclusive).",
                    "starter_code": "n = 5\n# Write a loop here\n",
                    "solution_code": "n = 5\nfor i in range(1, n + 1):\n    print(i)",
                    "test_cases": [
                        {"input": {"n": 5}, "expected_output": "1\n2\n3\n4\n5\n"},
                        {"input": {"n": 3}, "expected_output": "1\n2\n3\n"},
                    ],
                    "hints": [
                        "Use range(start, end+1) for inclusive range",
                        "range(1, n+1) gives 1, 2, ..., n"
                    ],
                    "estimated_minutes": 8,
                    "points": 12
                }
            ],
            "intermediate": [
                {
                    "title": "Sum of Even Numbers",
                    "description": "Calculate the sum of all even numbers from 1 to n.",
                    "starter_code": "n = 10\n# Write code to sum even numbers from 1 to n\n",
                    "solution_code": "n = 10\ntotal = 0\nfor i in range(2, n + 1, 2):\n    total += i\nprint(total)",
                    "test_cases": [
                        {"input": {"n": 10}, "expected_output": "30\n"},
                        {"input": {"n": 5}, "expected_output": "6\n"},
                    ],
                    "hints": [
                        "Use range(start, end, step) with step=2",
                        "Or use if i % 2 == 0 inside loop"
                    ],
                    "estimated_minutes": 12,
                    "points": 20
                }
            ]
        },
        "conditional": {
            "beginner": [
                {
                    "title": "Even or Odd Checker",
                    "description": "Write a program that checks if a number is even or odd.",
                    "starter_code": "number = 7\n# Write if/else to check even or odd\n",
                    "solution_code": "number = 7\nif number % 2 == 0:\n    print(\"Even\")\nelse:\n    print(\"Odd\")",
                    "test_cases": [
                        {"input": {"number": 7}, "expected_output": "Odd\n"},
                        {"input": {"number": 4}, "expected_output": "Even\n"},
                    ],
                    "hints": ["Use modulo operator %", "Even numbers have remainder 0 when divided by 2"],
                    "estimated_minutes": 8,
                    "points": 12
                }
            ]
        },
        "list": {
            "beginner": [
                {
                    "title": "Find Maximum in List",
                    "description": "Write a function to find the maximum value in a list without using max().",
                    "starter_code": "def find_max(numbers):\n    # Find and return maximum\n    pass\n\nprint(find_max([3, 1, 4, 1, 5, 9, 2]))",
                    "solution_code": "def find_max(numbers):\n    if not numbers:\n        return None\n    max_val = numbers[0]\n    for num in numbers:\n        if num > max_val:\n            max_val = num\n    return max_val\n\nprint(find_max([3, 1, 4, 1, 5, 9, 2]))",
                    "test_cases": [
                        {"input": {"numbers": [3, 1, 4, 1, 5, 9, 2]}, "expected_output": "9\n"},
                        {"input": {"numbers": [10, 5, 8]}, "expected_output": "10\n"},
                    ],
                    "hints": ["Initialize max with first element", "Compare each element with current max"],
                    "estimated_minutes": 15,
                    "points": 20
                }
            ]
        }
    }
    
    def generate_exercises(self, request: ExerciseRequest) -> List[Exercise]:
        """Generate exercises based on request"""
        exercises = []
        
        # Get templates for topic
        topic_templates = self.EXERCISE_TEMPLATES.get(request.topic, {})
        difficulty_templates = topic_templates.get(request.difficulty.value, [])
        
        # If no specific templates, use generic ones
        if not difficulty_templates:
            difficulty_templates = self._get_generic_templates(request.topic, request.difficulty)
        
        # Filter by type if specified
        if request.type:
            difficulty_templates = [t for t in difficulty_templates if t.get("type", "function_implementation") == request.type.value]
        
        # Generate requested number of exercises
        for i in range(min(request.count, len(difficulty_templates))):
            template = difficulty_templates[i % len(difficulty_templates)]
            exercise = self._create_exercise_from_template(
                template, request.topic, request.difficulty, request.subtopic
            )
            exercises.append(exercise)
        
        # If we need more than templates, create variations
        while len(exercises) < request.count:
            template = difficulty_templates[len(exercises) % len(difficulty_templates)]
            exercise = self._create_variation(exercises[-1], template)
            exercises.append(exercise)
        
        return exercises[:request.count]
    
    def _get_generic_templates(self, topic: str, difficulty: DifficultyLevel) -> List[Dict]:
        """Generate generic templates when specific ones not available"""
        return [{
            "title": f"Practice {topic.capitalize()}",
            "description": f"Practice exercise for {topic} at {difficulty.value} level",
            "starter_code": f"# Practice {topic} here\npass",
            "solution_code": f"# Solution for {topic}\npass",
            "test_cases": [{"input": {}, "expected_output": ""}],
            "hints": [f"Review {topic} concepts"],
            "estimated_minutes": 15,
            "points": 20
        }]
    
    def _create_exercise_from_template(self, template: Dict, topic: str, 
                                       difficulty: DifficultyLevel, subtopic: Optional[str]) -> Exercise:
        return Exercise(
            id=str(uuid.uuid4()),
            title=template["title"],
            description=template["description"],
            difficulty=difficulty,
            type=template.get("type", ExerciseType.FUNCTION_IMPLEMENTATION),
            topic=topic,
            subtopic=subtopic,
            starter_code=template["starter_code"],
            solution_code=template["solution_code"],
            test_cases=[TestCase(**tc) for tc in template.get("test_cases", [])],
            hints=template.get("hints", []),
            estimated_minutes=template.get("estimated_minutes", 15),
            points=template.get("points", 20),
            prerequisites=template.get("prerequisites", []),
            tags=[topic, difficulty.value]
        )
    
    def _create_variation(self, base_exercise: Exercise, template: Dict) -> Exercise:
        """Create a variation of an existing exercise"""
        return Exercise(
            id=str(uuid.uuid4()),
            title=f"{template['title']} (Variant)",
            description=template["description"],
            difficulty=base_exercise.difficulty,
            type=base_exercise.type,
            topic=base_exercise.topic,
            subtopic=base_exercise.subtopic,
            starter_code=template["starter_code"],
            solution_code=template["solution_code"],
            test_cases=[TestCase(**tc) for tc in template.get("test_cases", [])],
            hints=template.get("hints", []),
            estimated_minutes=template.get("estimated_minutes", 15),
            points=template.get("points", 20),
            prerequisites=template.get("prerequisites", []),
            tags=base_exercise.tags
        )


exercise_generator = ExerciseGenerator()


# ============================================
# Code Execution & Grading
# ============================================

class CodeExecutor:
    """Execute and grade student code"""
    
    @staticmethod
    def run_test(student_code: str, test_case: TestCase) -> TestResult:
        """Run a single test case against student code"""
        # Prepare test code
        test_code = f"""
{student_code}

# Test execution
import json
import sys

try:
    # Prepare input
    test_input = {json.dumps(test_case.input)}
    
    # Call the function if it's a function implementation
    # This is simplified - real implementation would be more sophisticated
    result = None
    
    # Capture output
    import io
    import contextlib
    
    output_buffer = io.StringIO()
    with contextlib.redirect_stdout(output_buffer):
        # Execute student code in a controlled way
        exec_globals = {}
        exec({json.dumps(student_code)}, exec_globals)
        
    output = output_buffer.getvalue()
    
    # Compare with expected
    expected = {json.dumps(test_case.expected_output)}
    # Normalize output
    if output.strip() == str(expected).strip():
        print("PASS")
    else:
        print(f"FAIL: Expected {{expected}}, got {{output.strip()}}")
        
except Exception as e:
    print(f"ERROR: {{e}}")
"""
        
        # Write to temp file and execute
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(textwrap.dedent(test_code))
            temp_file = f.name
        
        try:
            start_time = time.time()
            result = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            execution_time = int((time.time() - start_time) * 1000)
            
            passed = "PASS" in result.stdout
            actual_output = result.stdout.strip()
            error = result.stderr if result.returncode != 0 else None
            
            return TestResult(
                test_case=test_case,
                passed=passed,
                actual_output=actual_output,
                error=error,
                execution_time_ms=0
            )
        except subprocess.TimeoutExpired:
            return TestResult(
                test_case=test_case,
                passed=False,
                actual_output="",
                error="Execution timed out (10s limit)",
                execution_time_ms=10000
            )
        except Exception as e:
            return TestResult(
                test_case=test_case,
                passed=False,
                actual_output="",
                error=str(e),
                execution_time_ms=0
            )
        finally:
            try:
                os.unlink(temp_file)
            except:
                pass


class CodeGrader:
    """Grade student submissions"""
    
    def __init__(self):
        self.executor = CodeExecutor()
    
    def grade(self, exercise: Exercise, student_code: str) -> SubmissionResult:
        """Grade a student submission"""
        test_results = []
        passed_count = 0
        
        for test_case in exercise.test_cases:
            result = self.executor.run_test(student_code, test_case)
            test_results.append(result)
            if result.passed:
                passed_count += 1
        
        # Calculate score
        score = (passed_count / len(exercise.test_cases)) * 100 if exercise.test_cases else 0
        passed = score == 100.0
        
        # Generate feedback
        feedback = self._generate_feedback(exercise, student_code, test_results)
        hints = self._generate_hints(exercise, test_results)
        concepts = self._identify_concepts(exercise, test_results)
        
        total_time = sum(r.execution_time_ms for r in test_results)
        
        return SubmissionResult(
            exercise_id=exercise.id,
            passed=passed,
            score=score,
            test_results=test_results,
            feedback=feedback,
            hints=hints,
            concepts_to_review=concepts,
            execution_time_ms=sum(r.execution_time_ms for r in test_results)
        )
    
    def _generate_feedback(self, exercise: Exercise, code: str, results: List[TestResult]) -> str:
        passed = sum(1 for r in results if r.passed)
        total = len(results)
        
        if passed == total:
            return "Excellent! All tests passed. Great job!"
        elif passed > 0:
            return f"Good progress! {passed}/{total} tests passed. Review the failing cases."
        else:
            return "None of the tests passed. Check your logic and try again."
    
    def _generate_hints(self, exercise: Exercise, results: List[TestResult]) -> List[str]:
        hints = []
        for i, result in enumerate(results):
            if not result.passed and exercise.hints:
                hints.append(exercise.hints[min(i, len(exercise.hints) - 1)])
        return hints
    
    def _identify_concepts(self, exercise: Exercise, results: List[TestResult]) -> List[str]:
        concepts = set()
        if any(not r.passed for r in results):
            concepts.update(exercise.tags)
            concepts.add(exercise.topic)
        return list(concepts)


exercise_generator = ExerciseGenerator()
code_grader = CodeGrader()


# ============================================
# API Endpoints
# ============================================

@app.post("/exercises/generate", response_model=GeneratedExercise)
async def generate_exercises(
    request: ExerciseRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Generate coding exercises based on topic and difficulty"""
    exercises = exercise_generator.generate_exercises(request)
    
    # Store exercises in state/redis for later retrieval
    for ex in exercises:
        await cache_set(f"exercise:{ex.id}", ex.model_dump(), 86400)
    
    # Publish event
    background_tasks.add_task(
        publish_event,
        "exercises.generated",
        "exercises_generated",
        {
            "student_id": current_user.get("sub"),
            "topic": request.topic,
            "difficulty": request.difficulty.value,
            "count": len(exercises)
        }
    )
    
    return GeneratedExercise(exercises=exercises)


@app.get("/exercises/{exercise_id}", response_model=Exercise)
async def get_exercise(exercise_id: str, current_user: dict = Depends(get_current_user)):
    """Get exercise by ID"""
    cached = await cache_get(f"exercise:{exercise_id}")
    if not cached:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return Exercise(**cached)


@app.post("/exercises/submit", response_model=SubmissionResult)
async def submit_exercise(
    request: SubmissionRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Submit code for an exercise and get graded results"""
    # Get exercise
    cached = await cache_get(f"exercise:{request.exercise_id}")
    if not cached:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    exercise = Exercise(**cached)
    student_id = current_user.get("sub") or request.student_id
    
    # Grade submission
    result = code_grader.grade(exercise, request.code)
    
    # Publish event
    background_tasks.add_task(
        publish_event,
        "exercise.submitted",
        "exercise_submitted",
        {
            "student_id": student_id,
            "exercise_id": request.exercise_id,
            "passed": result.passed,
            "score": result.score
        }
    )
    
    return result


@app.get("/exercises/list")
async def list_exercises(
    topic: Optional[str] = None,
    difficulty: Optional[DifficultyLevel] = None,
    type: Optional[ExerciseType] = None,
    current_user: dict = Depends(get_current_user)
):
    """List available exercises (mock - in production would query database)"""
    return {
        "exercises": [],
        "total": 0,
        "message": "Use /exercises/generate to create exercises"
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="healthy",
        service="exercise-agent",
        checks={"database": True, "redis": True, "dapr": True}
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)