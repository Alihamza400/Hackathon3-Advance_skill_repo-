export type UserRole = 'student' | 'teacher' | 'admin'

export interface User {
  id: string
  email: string
  full_name: string
  role: UserRole
  status: 'active' | 'inactive' | 'pending_verification' | 'suspended'
  email_verified: boolean
  avatar_url?: string
  timezone: string
  language: string
  created_at: string
  last_login_at?: string
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: User
}

export type QueryType = 'explain' | 'debug' | 'code_review' | 'exercise' | 'progress' | 'general'

export interface TriageRequest {
  query: string
  context?: Record<string, unknown>
  student_id?: string
  session_id?: string
}

export interface TriageResponse {
  query_type: QueryType
  confidence: number
  routed_to: string
  reasoning: string
  suggested_prompt?: string
  metadata: Record<string, unknown>
}

export type DifficultyLevel = 'beginner' | 'intermediate' | 'advanced'

export interface CodeExample {
  title: string
  code: string
  explanation: string
  language: string
}

export interface ConceptExplanation {
  concept: string
  level: DifficultyLevel
  definition: string
  explanation: string
  key_points: string[]
  analogies: string[]
  code_examples: CodeExample[]
  common_mistakes: string[]
  related_concepts: string[]
  practice_exercises: { title: string; description: string }[]
  prerequisites: string[]
  next_steps: string[]
  estimated_reading_time_minutes: number
}

export interface ExplainResponse {
  explanation: ConceptExplanation
  follow_up_suggestions: string[]
  related_topics: string[]
}

export type ExerciseType = 'code_completion' | 'bug_fix' | 'function_implementation' | 'algorithm' | 'debug' | 'code_review'

export interface TestCase {
  input: Record<string, unknown>
  expected_output: unknown
  description?: string
  hidden: boolean
}

export interface Exercise {
  id: string
  title: string
  description: string
  type: ExerciseType
  difficulty: DifficultyLevel
  topic: string
  starter_code?: string
  test_cases: TestCase[]
  hints: string[]
  solution?: string
  time_estimate_minutes: number
}

export interface ExerciseSubmission {
  exercise_id: string
  code: string
  language?: string
}

export interface TestResult {
  passed: boolean
  description?: string
  input?: string
  expected: string
  actual: string
  error?: string
}

export interface ExerciseResult {
  passed: boolean
  score: number
  total_tests: number
  passed_tests: number
  results: TestResult[]
  feedback: string
  hints_used: number
  time_spent_seconds: number
}

export type MasteryLevel = 'beginner' | 'learning' | 'proficient' | 'mastered'

export interface ConceptMastery {
  concept: string
  mastery_level: MasteryLevel
  score: number
  exercises_attempted: number
  exercises_passed: number
  last_practiced?: string
}

export interface ProgressEvent {
  id: string
  event_type: string
  user_id: string
  concept?: string
  metadata: Record<string, unknown>
  created_at: string
}

export interface StreakInfo {
  current_streak: number
  longest_streak: number
  last_activity_date?: string
  streak_ended_at?: string
}

export interface DashboardData {
  overall_mastery: number
  streak: StreakInfo
  recent_activity: ProgressEvent[]
  concepts_mastered: number
  total_exercises: number
  passed_exercises: number
  concept_mastery: ConceptMastery[]
  suggested_topics: string[]
}

export type Severity = 'info' | 'warning' | 'error' | 'critical'
export type IssueCategory = 'syntax' | 'style' | 'performance' | 'security' | 'best_practice' | 'bug_risk' | 'maintainability'

export interface ReviewIssue {
  line: number
  column?: number
  severity: Severity
  category: IssueCategory
  message: string
  suggestion?: string
  code?: string
}

export interface CodeReviewResponse {
  issues: ReviewIssue[]
  summary: {
    total_issues: number
    by_severity: Record<string, number>
    by_category: Record<string, number>
    overall_score: number
  }
  metrics?: {
    lines_of_code: number
    complexity: number
    maintainability_index: number
    halstead_metrics?: Record<string, number>
  }
}

export type ErrorType = 'syntax_error' | 'runtime_error' | 'logic_error' | 'type_error' | 'name_error' | 'index_error' | 'key_error' | 'attribute_error' | 'value_error' | 'zero_division_error' | 'import_error' | 'assertion_error' | 'timeout' | 'memory_error' | 'unknown'

export interface DebugResult {
  error_type: ErrorType
  error_message: string
  line_number?: number
  explanation: string
  suggestion: string
  fixed_code?: string
  hints: string[]
  similar_errors: { error: string; solution: string }[]
}

export interface CodeExecutionResult {
  stdout: string
  stderr: string
  exit_code: number
  execution_time_ms: number
  output: string
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
  metadata?: Record<string, unknown>
}

export interface ChatSession {
  id: string
  title: string
  messages: ChatMessage[]
  created_at: string
  updated_at: string
}
