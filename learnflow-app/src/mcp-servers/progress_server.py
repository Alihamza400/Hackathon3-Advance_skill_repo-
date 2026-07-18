import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("progress_server")

app = FastAPI(title="Progress Monitoring MCP Server", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MOCK_DATA = {
    "student_001": {
        "name": "Maya Patel",
        "progress_summary": {
            "overall_mastery": 72.5,
            "modules_completed": 4,
            "total_modules": 8,
            "current_module": "Module 5: OOP",
            "current_module_progress": 45.0,
            "exercises_completed": 47,
            "quizzes_taken": 18,
            "average_quiz_score": 76.3,
            "streak_days": 5,
            "last_active": "2026-07-17T14:30:00Z",
        },
        "mastery": {
            "Module 1: Basics": 92.0,
            "Module 2: Control Flow": 88.5,
            "Module 3: Data Structures": 75.0,
            "Module 4: Functions": 65.0,
            "Module 5: OOP": 35.0,
            "Module 6: Files": 0.0,
            "Module 7: Errors": 0.0,
            "Module 8: Libraries": 0.0,
        },
        "struggles": [
            {
                "area": "Nested Loops",
                "module": "Module 2: Control Flow",
                "type": "same_error_3x",
                "detail": "IndexError in nested loop patterns 3 times",
                "severity": "medium",
                "detected_at": "2026-07-15T10:30:00Z",
                "suggested_action": "Review nested loop patterns",
            },
            {
                "area": "Dictionary Methods",
                "module": "Module 3: Data Structures",
                "type": "quiz_score_below_50",
                "detail": "Quiz score 42% on dictionary operations",
                "severity": "high",
                "detected_at": "2026-07-16T09:15:00Z",
                "suggested_action": "Reinforce dictionary methods with practice exercises",
            },
        ],
    },
    "student_002": {
        "name": "James Chen",
        "progress_summary": {
            "overall_mastery": 45.0,
            "modules_completed": 2,
            "total_modules": 8,
            "current_module": "Module 3: Data Structures",
            "current_module_progress": 30.0,
            "exercises_completed": 22,
            "quizzes_taken": 8,
            "average_quiz_score": 58.0,
            "streak_days": 2,
            "last_active": "2026-07-17T11:00:00Z",
        },
        "mastery": {
            "Module 1: Basics": 78.0,
            "Module 2: Control Flow": 62.0,
            "Module 3: Data Structures": 25.0,
            "Module 4: Functions": 0.0,
            "Module 5: OOP": 0.0,
            "Module 6: Files": 0.0,
            "Module 7: Errors": 0.0,
            "Module 8: Libraries": 0.0,
        },
        "struggles": [
            {
                "area": "List Comprehensions",
                "module": "Module 3: Data Structures",
                "type": "same_error_3x",
                "detail": "SyntaxError on list comprehensions 4 times",
                "severity": "high",
                "detected_at": "2026-07-17T10:00:00Z",
                "suggested_action": "Create easy exercises on list comprehensions",
            },
            {
                "area": "While Loops",
                "module": "Module 2: Control Flow",
                "type": "stuck_over_10min",
                "detail": "Spent 15 minutes on while loop exercise",
                "severity": "medium",
                "detected_at": "2026-07-14T16:45:00Z",
                "suggested_action": "Review while loop conditions and break statements",
            },
        ],
    },
}


def get_student(student_id: str):
    if student_id not in MOCK_DATA:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
    return MOCK_DATA[student_id]


@app.get("/health")
async def health():
    return {"status": "ok", "service": "progress-mcp-server"}


@app.get("/mcp/progress/{student_id}")
async def get_student_progress(student_id: str):
    student = get_student(student_id)
    return {
        "student_id": student_id,
        "name": student["name"],
        "progress": student["progress_summary"],
    }


@app.get("/mcp/progress/{student_id}/mastery")
async def get_student_mastery(student_id: str):
    student = get_student(student_id)
    return {
        "student_id": student_id,
        "name": student["name"],
        "mastery": student["mastery"],
    }


@app.get("/mcp/progress/{student_id}/struggles")
async def get_student_struggles(student_id: str):
    student = get_student(student_id)
    return {
        "student_id": student_id,
        "name": student["name"],
        "struggles": student["struggles"],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8102)
