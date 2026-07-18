import axios, { AxiosError, type AxiosInstance, type InternalAxiosRequestConfig } from 'axios'
import type {
  AuthTokens,
  User,
  TriageRequest,
  TriageResponse,
  ExplainResponse,
  DifficultyLevel,
  Exercise,
  ExerciseResult,
  ExerciseSubmission,
  DashboardData,
  CodeReviewResponse,
  DebugResult,
  CodeExecutionResult,
  ConceptMastery,
  StreakInfo,
  ProgressEvent,
} from '@/types'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api'

class ApiClient {
  private client: AxiosInstance
  private refreshPromise: Promise<AuthTokens> | null = null

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE,
      timeout: 30000,
      headers: { 'Content-Type': 'application/json' },
    })

    this.client.interceptors.request.use(this.authInterceptor.bind(this))
    this.client.interceptors.response.use(
      response => response,
      this.errorInterceptor.bind(this)
    )
  }

  private authInterceptor(config: InternalAxiosRequestConfig) {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
    }
    return config
  }

  private async errorInterceptor(error: AxiosError) {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const tokens = await this.refreshTokens()
        originalRequest.headers.Authorization = `Bearer ${tokens.access_token}`
        return this.client(originalRequest)
      } catch {
        if (typeof window !== 'undefined') {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    }

    return Promise.reject(error)
  }

  private async refreshTokens(): Promise<AuthTokens> {
    if (this.refreshPromise) return this.refreshPromise

    this.refreshPromise = new Promise(async (resolve, reject) => {
      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (!refreshToken) throw new Error('No refresh token')

        const { data } = await axios.post(`${API_BASE}/auth/refresh`, { refresh_token: refreshToken })
        localStorage.setItem('access_token', data.access_token)
        localStorage.setItem('refresh_token', data.refresh_token)
        resolve(data)
      } catch (e) {
        reject(e)
      } finally {
        this.refreshPromise = null
      }
    })

    return this.refreshPromise
  }

  setTokens(tokens: AuthTokens) {
    localStorage.setItem('access_token', tokens.access_token)
    localStorage.setItem('refresh_token', tokens.refresh_token)
  }

  clearTokens() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  getStoredToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('access_token')
    }
    return null
  }

  isAuthenticated(): boolean {
    return !!this.getStoredToken()
  }

  // Auth
  async login(email: string, password: string): Promise<AuthTokens> {
    const formData = new URLSearchParams()
    formData.append('username', email)
    formData.append('password', password)
    const { data } = await axios.post(`${API_BASE}/auth/login`, formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    this.setTokens(data)
    return data
  }

  async register(fullName: string, email: string, password: string, role: string = 'student'): Promise<User> {
    const { data } = await axios.post(`${API_BASE}/auth/register`, { full_name: fullName, email, password, role })
    return data
  }

  async logout() {
    try {
      const refreshToken = localStorage.getItem('refresh_token')
      await axios.post(`${API_BASE}/auth/logout`, { refresh_token: refreshToken }, {
        headers: { Authorization: `Bearer ${this.getStoredToken()}` },
      })
    } finally {
      this.clearTokens()
    }
  }

  async getProfile(): Promise<User> {
    const { data } = await this.client.get('/auth/me')
    return data
  }

  async updateProfile(updates: Partial<User>): Promise<User> {
    const { data } = await this.client.patch('/auth/me', updates)
    return data
  }

  // Triage
  async triageQuery(request: TriageRequest): Promise<TriageResponse> {
    const { data } = await this.client.post('/triage', request)
    return data
  }

  async routeQuery(request: TriageRequest): Promise<{ triage: TriageResponse; agent_response: unknown }> {
    const { data } = await this.client.post('/triage/route', request)
    return data
  }

  // Concepts
  async explainConcept(concept: string, level: DifficultyLevel = 'beginner', context?: string): Promise<ExplainResponse> {
    const { data } = await this.client.post('/concepts/explain', { concept, level, context })
    return data
  }

  async listConcepts(level?: DifficultyLevel) {
    const params = level ? { level } : {}
    const { data } = await this.client.get('/concepts/list', { params })
    return data
  }

  // Code Review
  async reviewCode(code: string): Promise<CodeReviewResponse> {
    const { data } = await this.client.post('/code-review/review', { code })
    return data
  }

  async checkSyntax(code: string) {
    const { data } = await this.client.post('/code-review/syntax', { code })
    return data
  }

  async getCodeMetrics(code: string) {
    const { data } = await this.client.post('/code-review/metrics', { code })
    return data
  }

  // Debug
  async debugCode(code: string, description?: string): Promise<DebugResult> {
    const { data } = await this.client.post('/debug', { code, description })
    return data
  }

  async executeCode(code: string, testInput?: string): Promise<CodeExecutionResult> {
    const { data } = await this.client.post('/debug/execute', { code, test_input: testInput })
    return data
  }

  async analyzeTraceback(traceback: string) {
    const { data } = await this.client.post('/debug/analyze', { traceback })
    return data
  }

  // Exercises
  async generateExercises(topic: string, difficulty: DifficultyLevel = 'beginner', count: number = 3): Promise<Exercise[]> {
    const { data } = await this.client.post('/exercises/generate', { topic, difficulty, count })
    return data.exercises || data
  }

  async getExercise(id: string): Promise<Exercise> {
    const { data } = await this.client.get(`/exercises/${id}`)
    return data
  }

  async submitExercise(submission: ExerciseSubmission): Promise<ExerciseResult> {
    const { data } = await this.client.post('/exercises/submit', submission)
    return data
  }

  // Progress
  async getDashboard(): Promise<DashboardData> {
    const { data } = await this.client.get('/progress/dashboard')
    return data
  }

  async getStreak(): Promise<StreakInfo> {
    const { data } = await this.client.get('/progress/streak')
    return data
  }

  async recordProgressEvent(event: { event_type: string; concept?: string; metadata?: Record<string, unknown> }) {
    const { data } = await this.client.post('/progress/events', event)
    return data
  }

  async getConceptMastery(): Promise<ConceptMastery[]> {
    const { data } = await this.client.get('/progress/concepts')
    return data
  }

  // Teacher
  async getTeacherDashboard() {
    const { data } = await this.client.get('/teacher/dashboard')
    return data
  }

  // Health
  async healthCheck() {
    const { data } = await this.client.get('/health')
    return data
  }

  async servicesStatus() {
    const { data } = await this.client.get('/services/status')
    return data
  }
}

export const api = new ApiClient()
