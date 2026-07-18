# API Reference

All endpoints are proxied through the API Gateway at `http://localhost:8000`.

## Auth Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login with email/password |
| POST | `/auth/refresh` | Refresh access token |
| POST | `/auth/logout` | Logout and revoke tokens |
| GET | `/auth/me` | Get current user profile |
| PATCH | `/auth/me` | Update user profile |
| POST | `/auth/change-password` | Change password |
| POST | `/auth/forgot-password` | Request password reset |
| POST | `/auth/reset-password` | Confirm password reset |
| POST | `/auth/verify-email` | Verify email address |

## Triage Endpoint

| Method | Path | Description |
|--------|------|-------------|
| POST | `/triage` | Classify a student query and route to appropriate agent |
| POST | `/triage/route` | Classify and forward query directly to specialist agent |

**Request Body**:
```json
{
  "query": "Explain how loops work in Python",
  "context": {"student_id": "user-123"},
  "session_id": "session-abc"
}
```

## Concepts Endpoint

| Method | Path | Description |
|--------|------|-------------|
| POST | `/concepts/explain` | Explain a Python concept at specified difficulty |
| GET | `/concepts/list` | List available concepts |

**Request Body**:
```json
{
  "concept": "function",
  "level": "beginner",
  "include_examples": true
}
```

## Code Review Endpoint

| Method | Path | Description |
|--------|------|-------------|
| POST | `/code-review/review` | Full code review with metrics |
| POST | `/code-review/syntax` | Quick syntax check |
| POST | `/code-review/metrics` | Code metrics only |

**Request Body**:
```json
{
  "code": "def add(a, b):\n    return a + b",
  "language": "python",
  "check_style": true,
  "check_security": true
}
```

## Debug Endpoint

| Method | Path | Description |
|--------|------|-------------|
| POST | `/debug` | Analyze code error and provide debugging hints |
| POST | `/debug/execute` | Execute code in sandboxed environment |
| POST | `/debug/analyze` | Analyze a traceback string |
| GET | `/error-types` | List supported error types |

**Request Body**:
```json
{
  "code": "print(x)",
  "error_message": "NameError: name 'x' is not defined",
  "test_input": null
}
```

## Exercise Endpoint

| Method | Path | Description |
|--------|------|-------------|
| POST | `/exercises/generate` | Generate coding exercises |
| GET | `/exercises/{id}` | Get exercise by ID |
| POST | `/exercises/submit` | Submit solution for grading |

**Request Body**:
```json
{
  "topic": "function",
  "difficulty": "beginner",
  "count": 1
}
```

## Progress Endpoint

| Method | Path | Description |
|--------|------|-------------|
| POST | `/progress/events` | Record a progress event |
| GET | `/progress/dashboard` | Get student dashboard |
| GET | `/progress/streak` | Get streak information |
| GET | `/progress/topic/{topic_id}` | Get topic-level progress |
| GET | `/progress/mastery/{topic_id}` | Get mastery calculation |
| GET | `/teacher/dashboard` | Get teacher dashboard |
