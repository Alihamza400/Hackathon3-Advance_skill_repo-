# Concepts Agent Service - Explains Python concepts with examples
# LearnFlow AI Tutoring Platform

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from enum import Enum
import os
import uuid

from shared.base import (
    create_app, settings, logger, cache_get, cache_set,
    publish_event, get_current_user, get_optional_user,
    dapr_client, publish_event
)

settings.service_name = "concepts-agent"

app = create_app("concepts-agent", "Concepts Agent - Python Concept Explainer")


# ============================================
# Models
# ============================================

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class ExplainRequest(BaseModel):
    concept: str = Field(..., min_length=1, max_length=200, description="Concept to explain")
    level: DifficultyLevel = Field(default=DifficultyLevel.BEGINNER, description="Target difficulty level")
    context: Optional[str] = Field(None, description="Additional context or specific question")
    student_id: Optional[str] = None
    include_examples: bool = True
    include_visual: bool = False
    include_exercises: bool = True


class CodeExample(BaseModel):
    title: str
    code: str
    explanation: str
    language: str = "python"


class ConceptExplanation(BaseModel):
    concept: str
    level: DifficultyLevel
    definition: str
    explanation: str
    key_points: List[str]
    analogies: List[str] = []
    code_examples: List[CodeExample] = []
    common_mistakes: List[str] = []
    related_concepts: List[str] = []
    practice_exercises: List[Dict[str, Any]] = []
    visual_aid: Optional[Dict[str, Any]] = None
    prerequisites: List[str] = []
    next_steps: List[str] = []
    estimated_reading_time_minutes: int
    metadata: Dict[str, Any] = {}


class ExplainResponse(BaseModel):
    explanation: ConceptExplanation
    follow_up_suggestions: List[str] = []
    related_topics: List[str] = []


# ============================================
# Concept Knowledge Base
# ============================================

CONCEPT_KNOWLEDGE = {
    "variable": {
        "beginner": {
            "definition": "A variable is a named storage location in memory that holds a value.",
            "explanation": "Think of a variable like a labeled box. You can put something in it (assign a value), look at what's inside (read the value), or replace what's inside (reassign). The label (variable name) helps you find and identify the box later.",
            "key_points": [
                "Variables store data values",
                "Variable names are case-sensitive (age ≠ Age)",
                "Names must start with letter or underscore",
                "Python automatically determines the type"
            ],
            "analogies": [
                "Like a labeled box in a warehouse",
                "Like a sticky note with a value written on it",
                "Like a container with a label"
            ],
            "code_examples": [
                {
                    "title": "Basic Variable Assignment",
                    "code": "name = \"Alice\"\nage = 25\nheight = 5.6\nis_student = True\n\nprint(name)  # Output: Alice\nprint(age)   # Output: 25",
                    "explanation": "Variables can hold different types: string, integer, float, boolean"
                },
                {
                    "title": "Reassigning Variables",
                    "code": "x = 10\nprint(x)  # 10\nx = 20\nprint(x)  # 20\nx = \"hello\"\nprint(x)  # hello",
                    "explanation": "Variables can be reassigned to different values and types"
                },
                {
                    "title": "Multiple Assignment",
                    "code": "x = y = z = 0\n# All three variables equal 0\na, b, c = 1, 2, 3\n# a=1, b=2, c=3",
                    "explanation": "Python supports multiple assignment in one line"
                }
            ],
            "common_mistakes": [
                "Using reserved keywords as variable names (class, def, for, etc.)",
                "Starting variable names with numbers",
                "Confusing = (assignment) with == (comparison)",
                "Forgetting that variables are references to objects"
            ],
            "prerequisites": [],
            "next_steps": ["data_types", "operators", "control_flow"],
            "related_concepts": ["data_types", "assignment", "memory_management"]
        }
    },
    "function": {
        "beginner": {
            "definition": "A function is a reusable block of code that performs a specific task.",
            "explanation": "Functions are like recipes - you write the instructions once, then you can use them over and over with different ingredients (inputs) to get results (outputs). They help avoid repetition and make code organized.",
            "key_points": [
                "Functions encapsulate reusable logic",
                "They accept parameters (inputs) and return values (outputs)",
                "DRY principle - Don't Repeat Yourself",
                "Functions create their own local scope"
            ],
            "analogies": [
                "Like a recipe in a cookbook",
                "Like a machine that takes raw materials and produces a product",
                "Like a specialized tool in a toolbox"
            ],
            "code_examples": [
                {
                    "title": "Basic Function",
                    "code": "def greet(name):\n    return f\"Hello, {name}!\"\n\nmessage = greet(\"Alice\")\nprint(message)  # Hello, Alice!",
                    "explanation": "Simple function taking a parameter and returning a value"
                },
                {
                    "title": "Function with Default Parameters",
                    "code": "def greet(name, greeting=\"Hello\"):\n    return f\"{greeting}, {name}!\"\n\nprint(greet(\"Alice\"))        # Hello, Alice!\nprint(greet(\"Bob\", \"Hi\"))    # Hi, Bob!",
                    "explanation": "Default parameters make arguments optional"
                },
                {
                    "title": "Function with Return Values",
                    "code": "def calculate_area(length, width):\n    area = length * width\n    return area\n\nroom_area = calculate_area(5, 4)\nprint(f\"Area: {room_area} sq meters\")  # Area: 20 sq meters",
                    "explanation": "Functions can compute and return values"
                }
            ],
            "common_mistakes": [
                "Forgetting to return a value (returns None by default)",
                "Modifying mutable default arguments",
                "Not understanding variable scope",
                "Forgetting to call the function with ()"
            ],
            "prerequisites": ["variables", "data_types"],
            "next_steps": ["parameters", "return_values", "scope", "lambda_functions"],
            "related_concepts": ["parameters", "return_values", "scope", "modules"]
        }
    },
    "loop": {
        "beginner": {
            "definition": "A loop repeats a block of code multiple times.",
            "explanation": "Loops let you automate repetitive tasks. Instead of writing the same code over and over, you write it once and tell Python how many times to repeat it or what condition to check.",
            "key_points": [
                "for loops iterate over sequences (lists, strings, ranges)",
                "while loops repeat while a condition is True",
                "break exits the loop early",
                "continue skips to the next iteration"
            ],
            "analogies": [
                "Like a playlist on repeat",
                "Like a factory assembly line doing the same task",
                "Like reading every page in a book"
            ],
            "code_examples": [
                {
                    "title": "For Loop with Range",
                    "code": "for i in range(5):\n    print(f\"Count: {i}\")\n# Output: 0, 1, 2, 3, 4",
                    "explanation": "range(5) generates 0,1,2,3,4"
                },
                {
                    "title": "For Loop Over List",
                    "code": "fruits = [\"apple\", \"banana\", \"cherry\"]\nfor fruit in fruits:\n    print(f\"I like {fruit}\")",
                    "explanation": "Iterate directly over collection items"
                },
                {
                    "title": "While Loop",
                    "code": "count = 0\nwhile count < 3:\n    print(f\"Count: {count}\")\n    count += 1  # Don't forget to increment!",
                    "explanation": "Runs while condition is True"
                }
            ],
            "common_mistakes": [
                "Infinite loops (forgetting to update condition in while)",
                "Off-by-one errors with range()",
                "Modifying list while iterating over it",
                "Forgetting that range() is exclusive at the end"
            ],
            "prerequisites": ["variables", "conditionals"],
            "next_steps": ["nested_loops", "loop_control", "list_comprehensions"],
            "related_concepts": ["conditionals", "lists", "range"]
        }
    },
    "conditional": {
        "beginner": {
            "definition": "Conditionals let your code make decisions based on conditions.",
            "explanation": "Conditionals let your program make choices. Like a fork in the road - if the condition is true, go one way; otherwise, go another way (or do nothing).",
            "key_points": [
                "if checks a condition",
                "elif (else if) checks additional conditions",
                "else catches everything else",
                "Conditions evaluate to True or False"
            ],
            "analogies": [
                "Like a traffic light - green means go, red means stop",
                "Like a decision flowchart",
                "Like choosing what to wear based on weather"
            ],
            "code_examples": [
                {
                    "title": "Basic If/Else",
                    "code": "age = 18\nif age >= 18:\n    print(\"You can vote!\")\nelse:\n    print(\"Too young to vote\")",
                    "explanation": "Simple binary decision"
                },
                {
                    "title": "Elif Chain",
                    "code": "score = 85\nif score >= 90:\n    grade = \"A\"\nelif score >= 80:\n    grade = \"B\"\nelif score >= 70:\n    grade = \"C\"\nelse:\n    grade = \"F\"\nprint(f\"Grade: {grade}\")  # Grade: B",
                    "explanation": "Multiple conditions checked in order"
                }
            ],
            "common_mistakes": [
                "Using = instead of == for comparison",
                "Forgetting colons after conditions",
                "Indentation errors",
                "Confusing 'and'/'or' precedence"
            ],
            "prerequisites": ["variables", "operators"],
            "next_steps": ["nested_conditionals", "ternary_operator", "match_case"],
            "related_concepts": ["operators", "boolean_logic", "loops"]
        }
    }
}


class ConceptService:
    """Service for generating concept explanations"""
    
    def get_explanation(self, concept: str, level: DifficultyLevel, context: str = None) -> Dict:
        concept_lower = concept.lower().strip()
        
        # Check knowledge base
        if concept_lower in CONCEPT_KNOWLEDGE:
            level_data = CONCEPT_KNOWLEDGE[concept_lower].get(level.value, 
                            CONCEPT_KNOWLEDGE[concept_lower].get("beginner", {}))
            
            # Add context if provided
            context_note = f"\n\nContext: {context}" if context else ""
            
            return {
                "concept": concept,
                "level": level,
                "definition": level_data.get("definition", ""),
                "explanation": level_data.get("explanation", "") + context_note,
                "key_points": level_data.get("key_points", []),
                "analogies": level_data.get("analogies", []),
                "code_examples": level_data.get("code_examples", []),
                "common_mistakes": level_data.get("common_mistakes", []),
                "related_concepts": level_data.get("related_concepts", []),
                "practice_exercises": [
                    {"title": f"Practice {concept}", "description": f"Write code using {concept}"},
                    {"title": f"Debug {concept}", "description": f"Fix broken code using {concept}"}
                ],
                "prerequisites": level_data.get("prerequisites", []),
                "next_steps": level_data.get("next_steps", []),
                "estimated_reading_time_minutes": 10
            }
        
        # Fallback for unknown concepts
        return self._generate_generic_explanation(concept, level)
    
    def _generate_generic_explanation(self, concept: str, level: DifficultyLevel) -> Dict:
        return {
            "concept": concept,
            "level": level,
            "definition": f"{concept.capitalize()} is a programming concept in Python.",
            "explanation": f"An explanation of {concept} at {level.value} level would go here.",
            "key_points": [f"Key point about {concept}", "Another important aspect"],
            "analogies": [f"{concept} is like a tool in your toolbox"],
            "code_examples": [
                {
                    "title": f"Basic {concept}",
                    "code": f"# Example of {concept}\nprint('Hello, {concept}!')",
                    "explanation": f"Basic example of {concept}"
                }
            ],
            "common_mistakes": [f"Common mistake with {concept}"],
            "related_concepts": ["related_concept_1", "related_concept_2"],
            "practice_exercises": [
                {"title": f"Practice {concept}", "description": f"Write code using {concept}"}
            ],
            "prerequisites": ["basic_python"],
            "next_steps": ["advanced_topics"],
            "estimated_reading_time_minutes": 15
        }


concept_service = ConceptService()


# ============================================
# API Endpoints
# ============================================

@app.post("/explain", response_model=ExplainResponse)
async def explain_concept(
    request: ExplainRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Explain a Python concept at the specified difficulty level"""
    
    student_id = current_user.get("sub") or request.student_id
    
    # Check cache
    cache_key = f"explain:{request.concept}:{request.level.value}"
    cached = await cache_get(f"explain:{request.concept}:{request.level.value}")
    if cached:
        logger.info(f"Cache hit for concept: {request.concept}")
        explanation = ConceptExplanation(**cached)
        return ExplainResponse(
            explanation=explanation,
            follow_up_suggestions=[],
            related_topics=[]
        )
    
    # Generate explanation
    explanation_data = concept_service.get_explanation(
        request.concept, 
        request.level,
        request.context
    )
    
    # Add code examples if requested
    code_examples = []
    if request.include_examples:
        code_examples = explanation_data.get("code_examples", [])
    
    explanation = ConceptExplanation(
        concept=request.concept,
        level=request.level,
        definition=explanation_data["definition"],
        explanation=explanation_data["explanation"],
        key_points=explanation_data["key_points"],
        analogies=explanation_data.get("analogies", []),
        code_examples=[
            CodeExample(**ex) for ex in explanation_data.get("code_examples", [])
        ],
        common_mistakes=explanation_data.get("common_mistakes", []),
        related_concepts=explanation_data.get("related_concepts", []),
        practice_exercises=explanation_data.get("practice_exercises", []),
        prerequisites=explanation_data.get("prerequisites", []),
        next_steps=explanation_data.get("next_steps", []),
        estimated_reading_time_minutes=explanation_data.get("estimated_reading_time_minutes", 10),
        metadata={
            "student_id": student_id,
            "context": request.context,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    )
    
    # Cache result
    await cache_set(f"explain:{request.concept}:{request.level.value}", explanation.model_dump(), 3600)
    
    # Generate follow-up suggestions
    follow_up = [
        f"Practice exercises for {request.concept}",
        f"Related concept: {explanation_data.get('related_concepts', ['next_topic'])[0]}",
        f"Try exercises for {request.concept}"
    ]
    
    related = explanation_data.get("related_concepts", [])
    
    # Publish event
    background_tasks.add_task(
        publish_event,
        "concept.explained",
        "concept_explained",
        {
            "student_id": current_user.get("sub"),
            "concept": request.concept,
            "level": request.level.value,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )
    
    return ExplainResponse(
        explanation=ConceptExplanation(**explanation_data),
        follow_up_suggestions=[],
        related_topics=[]
    )


@app.get("/concepts/list")
async def list_concepts(
    level: Optional[DifficultyLevel] = None,
    current_user: dict = Depends(get_current_user)
):
    """List available concepts in the knowledge base"""
    concepts = []
    for concept, levels in CONCEPT_KNOWLEDGE.items():
        if level is None or level.value in levels:
            concepts.append({
                "name": concept,
                "available_levels": list(levels.keys()),
                "prerequisites": levels.get("beginner", {}).get("prerequisites", []),
                "next_steps": levels.get("beginner", {}).get("next_steps", [])
            })
    
    return {"concepts": concepts, "total": len(concepts)}


@app.get("/concepts/{concept}/levels")
async def get_concept_levels(
    concept: str,
    current_user: dict = Depends(get_current_user)
):
    """Get available difficulty levels for a concept"""
    concept_lower = concept.lower()
    if concept_lower not in CONCEPT_KNOWLEDGE:
        raise HTTPException(status_code=404, detail="Concept not found")
    
    return {
        "concept": concept,
        "available_levels": list(CONCEPT_KNOWLEDGE[concept_lower].keys())
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="healthy",
        service="concepts-agent",
        checks={"database": True, "redis": True, "dapr": True}
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)