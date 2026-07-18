# Progress Agent Service - Tracks student progress and mastery
# LearnFlow AI Tutoring Platform

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from enum import Enum
import uuid
from datetime import datetime, timezone, timedelta

from shared.base import (
    create_app, settings, logger, cache_get, cache_set,
    publish_event, get_current_user, get_optional_user,
    HealthResponse, PaginationParams, PaginatedResponse
)

settings.service_name = "progress-agent"

app = create_app("progress-agent", "Progress Agent - Student Progress Tracking")


# ============================================
# Models
# ============================================

class MasteryLevel(str, Enum):
    BEGINNER = "beginner"
    LEARNING = "learning"
    PROFICIENT = "proficient"
    MASTERED = "mastered"


class ProgressEventType(str, Enum):
    LESSON_STARTED = "lesson_started"
    LESSON_COMPLETED = "lesson_completed"
    EXERCISE_ATTEMPTED = "exercise_attempted"
    EXERCISE_PASSED = "exercise_passed"
    EXERCISE_FAILED = "exercise_failed"
    QUIZ_TAKEN = "quiz_taken"
    QUIZ_PASSED = "quiz_passed"
    QUIZ_FAILED = "quiz_failed"
    TOPIC_MASTERED = "topic_mastered"
    STRUGGLE_DETECTED = "struggle_detected"
    STREAK_EXTENDED = "streak_extended"
    STREAK_BROKEN = "streak_broken"
    STREAK_RECOVERED = "streak_recovered"
    LEVEL_UP = "level_up"


class ProgressEvent(BaseModel):
    id: str
    student_id: str
    event_type: str
    topic_id: Optional[str] = None
    lesson_id: Optional[str] = None
    exercise_id: Optional[str] = None
    quiz_id: Optional[str] = None
    metadata: Dict[str, Any] = {}
    timestamp: datetime


class TopicProgress(BaseModel):
    topic_id: str
    topic_title: str
    status: str  # not_started, in_progress, completed, mastered
    mastery_level: str
    mastery_score: float = Field(ge=0.0, le=100.0)
    exercise_completion_rate: float = Field(ge=0.0, le=100.0)
    quiz_average_score: float = Field(ge=0.0, le=100.0)
    code_quality_score: float = Field(ge=0.0, le=100.0)
    consistency_streak_days: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    last_accessed_at: datetime
    total_time_minutes: int = 0


class StudentDashboard(BaseModel):
    student_id: str
    full_name: str
    overall_mastery_score: float
    current_level: str
    total_study_minutes: int
    topics_completed: int
    topics_mastered: int
    current_streak_days: int
    longest_streak_days: int
    topics: List[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]
    upcoming_milestones: List[Dict[str, Any]]
    struggle_alerts: int
    weekly_goal_progress: float


class TeacherDashboard(BaseModel):
    class_id: str
    class_name: str
    total_students: int
    active_students_today: int
    avg_mastery_score: float
    total_struggle_alerts: int
    students: List[Dict[str, Any]]
    recent_alerts: List[Dict[str, Any]]


class ProgressEventRequest(BaseModel):
    student_id: Optional[str] = None
    event_type: str
    topic_id: Optional[str] = None
    lesson_id: Optional[str] = None
    exercise_id: Optional[str] = None
    quiz_id: Optional[str] = None
    metadata: Dict[str, Any] = {}


class StreakInfo(BaseModel):
    current_streak: int
    longest_streak: int
    last_activity_date: Optional[datetime]
    streak_status: Literal["active", "at_risk", "broken"]
    days_until_break: int


# ============================================
# Progress Engine
# ============================================

class ProgressEngine:
    """Core engine for tracking and calculating student progress"""
    
    MASTERY_THRESHOLDS = {
        "beginner": 0,
        "learning": 40,
        "proficient": 70,
        "mastered": 90
    }
    
    MASTERY_WEIGHTS = {
        "exercise_completion": 0.40,
        "quiz_score": 0.30,
        "code_quality": 0.20,
        "consistency": 0.10
    }
    
    async def record_event(self, event: ProgressEventRequest, student_id: str) -> Dict[str, Any]:
        """Record a progress event"""
        event_obj = {
            "id": str(uuid.uuid4()),
            "student_id": student_id,
            "event_type": event.event_type,
            "topic_id": event.topic_id,
            "lesson_id": event.lesson_id,
            "exercise_id": event.exercise_id,
            "quiz_id": event.quiz_id,
            "metadata": event.metadata,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Store event (in production, write to database)
        event_key = f"progress:events:{student_id}:{event_obj['id']}"
        await cache_set(event_key, event_obj, 86400 * 30)
        
        # Update topic progress
        if event.topic_id:
            await self.update_topic_progress(student_id, event.topic_id, event.event_type)
        
        # Update streak
        await self.update_streak(student_id)
        
        # Check for struggle patterns
        if event.event_type in [
            "exercise_failed", "quiz_failed", "struggle_detected"
        ]:
            await self.check_struggle_patterns(student_id)
        
        # Publish event
        await publish_event(
            "progress.event",
            event.event_type,
            {
                "student_id": student_id,
                "topic_id": event.topic_id,
                "event_type": event.event_type,
                "metadata": event.metadata
            }
        )
        
        return event_obj
    
    async def update_topic_progress(self, student_id: str, topic_id: str, 
                                   event_type: str) -> Dict[str, Any]:
        """Update and recalculate topic progress"""
        # In production, would query database for student's topic progress
        # For now, return mock data
        progress = {
            "topic_id": topic_id,
            "topic_title": f"Topic {topic_id}",
            "status": "in_progress",
            "mastery_level": "learning",
            "mastery_score": 45.0,
            "exercise_completion_rate": 40.0,
            "quiz_average_score": 65.0,
            "code_quality_score": 70.0,
            "consistency_streak_days": 5,
            "last_accessed_at": datetime.now(timezone.utc).isoformat(),
            "total_time_minutes": 120
        }
        
        progress_key = f"progress:topic:{student_id}:{topic_id}"
        await cache_set(f"progress:topic:{student_id}:{topic_id}", progress, 86400)
        
        return progress
    
    async def calculate_mastery(self, student_id: str, topic_id: str) -> Dict[str, Any]:
        """Calculate mastery score for a topic"""
        # Mock calculation - in production would query actual data
        exercise_completion = 65.0
        quiz_average = 72.0
        code_quality = 75.0
        consistency = 60.0
        
        mastery_score = (
            0.40 * exercise_completion +
            0.30 * quiz_average +
            0.20 * code_quality +
            0.10 * consistency
        )
        
        if mastery_score >= 90:
            level = "mastered"
        elif mastery_score >= 70:
            level = "proficient"
        elif mastery_score >= 40:
            level = "learning"
        else:
            level = "beginner"
        
        return {
            "mastery_score": round(mastery_score, 1),
            "mastery_level": level,
            "components": {
                "exercise_completion": 65.0,
                "quiz_average": 72.0,
                "code_quality": 75.0,
                "consistency": 60.0
            }
        }
    
    async def update_streak(self, student_id: str) -> Dict[str, Any]:
        """Update and calculate student streak"""
        # In production, would query daily metrics
        current_streak = 7
        longest_streak = 14
        last_activity = datetime.now(timezone.utc) - timedelta(days=1)
        
        return {
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "last_activity_date": last_activity.isoformat(),
            "streak_status": "active",
            "days_until_break": 0
        }
    
    async def get_streak_info(self, student_id: str) -> Dict[str, Any]:
        """Get current streak information"""
        return await self.update_streak(student_id)
    
    async def check_struggle_patterns(self, student_id: str) -> List[Dict]:
        """Check for struggle patterns and create alerts"""
        alerts = []
        
        # Mock check for repeated failures
        alerts.append({
            "type": "repeated_failures",
            "severity": "medium",
            "message": "Multiple failed attempts detected",
            "count": 3,
            "time_window": "1 hour"
        })
        
        return alerts
    
    async def get_student_dashboard(self, student_id: str) -> Dict[str, Any]:
        """Get comprehensive student dashboard"""
        # Mock data - in production would query database
        topics = [
            {
                "topic_id": "variables",
                "topic_title": "Variables & Data Types",
                "status": "mastered",
                "mastery_level": "mastered",
                "mastery_score": 95.0,
                "exercise_completion_rate": 100.0,
                "quiz_average_score": 92.0,
                "code_quality_score": 90.0,
                "consistency_streak_days": 10,
                "started_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "completed_at": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat(),
                "last_accessed_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                "total_time_minutes": 180
            },
            {
                "topic_id": "functions",
                "topic_title": "Functions",
                "status": "mastered",
                "mastery_level": "mastered",
                "mastery_score": 88.0,
                "exercise_completion_rate": 100.0,
                "quiz_average_score": 85.0,
                "code_quality_score": 85.0,
                "consistency_streak_days": 7,
                "started_at": (datetime.now(timezone.utc) - timedelta(days=20)).isoformat(),
                "completed_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
                "last_accessed_at": (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat(),
                "total_time_minutes": 220
            },
            {
                "topic_id": "loops",
                "topic_title": "Loops",
                "status": "proficient",
                "mastery_level": "proficient",
                "mastery_score": 78.0,
                "exercise_completion_rate": 90.0,
                "quiz_average_score": 75.0,
                "code_quality_score": 80.0,
                "consistency_streak_days": 5,
                "started_at": (datetime.now(timezone.utc) - timedelta(days=14)).isoformat(),
                "last_accessed_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
                "total_time_minutes": 180
            },
            {
                "topic_id": "conditionals",
                "topic_title": "Conditionals",
                "status": "learning",
                "mastery_level": "learning",
                "mastery_score": 55.0,
                "exercise_completion_rate": 60.0,
                "quiz_average_score": 65.0,
                "code_quality_score": 60.0,
                "consistency_streak_days": 3,
                "started_at": (datetime.now(timezone.utc) - timedelta(days=7)).isoformat(),
                "last_accessed_at": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat(),
                "total_time_minutes": 90
            }
        ]
        
        return {
            "student_id": student_id,
            "full_name": "Demo Student",
            "overall_mastery_score": 79.0,
            "current_level": "Intermediate",
            "total_study_minutes": 670,
            "topics_completed": 2,
            "topics_mastered": 2,
            "current_streak": 7,
            "longest_streak": 14,
            "topics": topics,
            "recent_activity": [
                {"type": "exercise_completed", "topic": "loops", "timestamp": "2024-01-15T10:30:00Z"},
                {"type": "quiz_passed", "topic": "functions", "score": 90, "timestamp": "2024-01-15T09:15:00Z"},
                {"type": "lesson_completed", "topic": "functions", "timestamp": "2024-01-14T15:20:00Z"}
            ],
            "upcoming_milestones": [
                {"title": "Master Conditionals", "progress": 55, "target": 70},
                {"title": "Reach 10-day Streak", "progress": 7, "target": 10}
            ],
            "struggle_alerts": 1,
            "weekly_goal_progress": 65.0
        }
    
    async def get_teacher_dashboard(self, teacher_id: str) -> Dict[str, Any]:
        """Get teacher dashboard for a class"""
        return {
            "class_id": "class-101",
            "class_name": "Python Fundamentals - Period 1",
            "total_students": 25,
            "active_students_today": 18,
            "avg_mastery_score": 72.5,
            "total_struggle_alerts": 3,
            "students": [
                {
                    "student_id": "student-1",
                    "name": "Alice Johnson",
                    "mastery_score": 85.0,
                    "current_topic": "functions",
                    "streak_days": 10,
                    "last_active": "2 hours ago",
                    "alerts": 0
                },
                {
                    "student_id": "student-2",
                    "name": "Bob Smith",
                    "mastery_score": 62.0,
                    "current_topic": "conditionals",
                    "streak_days": 2,
                    "last_active": "1 day ago",
                    "alerts": 1
                }
            ],
            "recent_alerts": [
                {
                    "student_name": "Charlie Brown",
                    "alert_type": "repeated_failures",
                    "severity": "high",
                    "timestamp": "2024-01-15T14:30:00Z"
                }
            ]
        }


progress_engine = ProgressEngine()


# ============================================
# API Endpoints
# ============================================

@app.post("/events", status_code=201)
async def record_event(
    event: ProgressEventRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Record a progress event"""
    student_id = current_user.get("sub") or event.student_id
    if not student_id:
        raise HTTPException(status_code=400, detail="Student ID required")
    
    event_obj = await progress_engine.record_event(event, student_id)
    
    return event_obj


@app.get("/progress/dashboard", response_model=Dict[str, Any])
async def get_dashboard(
    current_user: dict = Depends(get_current_user)
):
    """Get student dashboard"""
    student_id = current_user.get("sub")
    dashboard = await progress_engine.get_student_dashboard(student_id)
    return dashboard


@app.get("/progress/streak")
async def get_streak(
    current_user: dict = Depends(get_current_user)
):
    """Get student streak info"""
    student_id = current_user.get("sub")
    streak = await progress_engine.get_streak_info(student_id)
    return streak


@app.get("/progress/topic/{topic_id}")
async def get_topic_progress(
    topic_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get progress for specific topic"""
    student_id = current_user.get("sub")
    progress = await progress_engine.update_topic_progress(student_id, topic_id, "viewed")
    return progress


@app.get("/progress/mastery/{topic_id}")
async def get_mastery(
    topic_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get mastery calculation for topic"""
    student_id = current_user.get("sub")
    mastery = await progress_engine.calculate_mastery(student_id, topic_id)
    return mastery


@app.get("/progress/events")
async def get_events(
    topic_id: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Get progress events for student"""
    student_id = current_user.get("sub")
    
    # In production, would query database
    events = []
    
    return {
        "events": events,
        "total": 0,
        "limit": limit
    }


# Teacher endpoints
@app.get("/teacher/dashboard")
async def teacher_dashboard(
    current_user: dict = Depends(get_current_user)
):
    """Get teacher dashboard"""
    # Check if user is teacher
    if "teacher" not in current_user.get("roles", []):
        raise HTTPException(status_code=403, detail="Teacher access required")
    
    teacher_id = current_user.get("sub")
    dashboard = await progress_engine.get_teacher_dashboard(teacher_id)
    return dashboard


@app.get("/progress/alerts")
async def get_alerts(
    severity: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get struggle alerts"""
    student_id = current_user.get("sub")
    alerts = await progress_engine.check_struggle_patterns(student_id)
    
    if severity:
        alerts = [a for a in alerts if a["severity"] == severity]
    
    return {"alerts": alerts, "total": len(alerts)}


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="healthy",
        service="progress-agent",
        checks={"database": True, "redis": True, "dapr": True}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)