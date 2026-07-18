-- LearnFlow PostgreSQL Initialization Script
-- Enterprise-grade schema for LearnFlow AI Tutoring Platform

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
DO $$ BEGIN CREATE EXTENSION IF NOT EXISTS "pgaudit"; EXCEPTION WHEN OTHERS THEN END; $$;

-- Create schemas
CREATE SCHEMA IF NOT EXISTS learnflow;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS audit;

-- Set search path
ALTER DATABASE learnflow SET search_path = learnflow, analytics, audit, public;

-- ============================================
-- CORE TABLES
-- ============================================

-- Users table (students and teachers)
CREATE TABLE learnflow.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'student', -- 'student', 'teacher', 'admin'
    avatar_url VARCHAR(500),
    timezone VARCHAR(50) DEFAULT 'UTC',
    language VARCHAR(10) DEFAULT 'en',
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    last_login_at TIMESTAMPTZ,
    last_login_ip VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_users_email ON learnflow.users(email);
CREATE INDEX idx_users_role ON learnflow.users(role);
CREATE INDEX idx_users_active ON learnflow.users(is_active);

-- Teachers table (extends users)
CREATE TABLE learnflow.teachers (
    user_id UUID PRIMARY KEY REFERENCES learnflow.users(id) ON DELETE CASCADE,
    school_name VARCHAR(255),
    subject_areas TEXT[],
    bio TEXT,
    years_experience INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Classes table
CREATE TABLE learnflow.classes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    teacher_id UUID NOT NULL REFERENCES learnflow.teachers(user_id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    subject VARCHAR(100) NOT NULL,
    grade_level VARCHAR(50),
    invite_code VARCHAR(20) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT true,
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_classes_teacher ON learnflow.classes(teacher_id);
CREATE INDEX idx_classes_invite_code ON learnflow.classes(invite_code);
CREATE INDEX idx_classes_active ON learnflow.classes(is_active);

-- Class enrollments
CREATE TABLE learnflow.class_enrollments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    class_id UUID NOT NULL REFERENCES learnflow.classes(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES learnflow.users(id) ON DELETE CASCADE,
    enrolled_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,
    UNIQUE(class_id, student_id)
);

CREATE INDEX idx_enrollments_class ON learnflow.class_enrollments(class_id);
CREATE INDEX idx_enrollments_student ON learnflow.class_enrollments(student_id);

-- ============================================
-- CURRICULUM TABLES
-- ============================================

-- Modules (top-level curriculum units)
CREATE TABLE learnflow.modules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    order_index INTEGER NOT NULL,
    estimated_hours DECIMAL(4,1),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Topics within modules
CREATE TABLE learnflow.topics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    module_id UUID NOT NULL REFERENCES learnflow.modules(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    order_index INTEGER NOT NULL,
    difficulty_level INTEGER NOT NULL DEFAULT 1, -- 1=beginner, 2=intermediate, 3=advanced
    estimated_minutes INTEGER,
    learning_objectives TEXT[],
    prerequisites UUID[],
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_topics_module ON learnflow.topics(module_id);
CREATE INDEX idx_topics_order ON learnflow.topics(module_id, order_index);

-- Lessons within topics
CREATE TABLE learnflow.lessons (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    topic_id UUID NOT NULL REFERENCES learnflow.topics(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content_markdown TEXT,
    content_html TEXT,
    order_index INTEGER NOT NULL,
    estimated_minutes INTEGER,
    lesson_type VARCHAR(50) DEFAULT 'theory', -- 'theory', 'practice', 'quiz', 'project'
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_lessons_topic ON learnflow.lessons(topic_id);
CREATE INDEX idx_lessons_order ON learnflow.lessons(topic_id, order_index);

-- Exercises within lessons
CREATE TABLE learnflow.exercises (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lesson_id UUID NOT NULL REFERENCES learnflow.lessons(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    starter_code TEXT,
    solution_code TEXT,
    test_cases JSONB,
    difficulty INTEGER DEFAULT 1,
    estimated_minutes INTEGER,
    hints TEXT[],
    tags TEXT[],
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_exercises_lesson ON learnflow.exercises(lesson_id);

-- Quizzes
CREATE TABLE learnflow.quizzes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lesson_id UUID NOT NULL REFERENCES learnflow.lessons(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    time_limit_minutes INTEGER,
    passing_score INTEGER DEFAULT 70,
    max_attempts INTEGER DEFAULT 3,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Quiz questions
CREATE TABLE learnflow.quiz_questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    quiz_id UUID NOT NULL REFERENCES learnflow.quizzes(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) NOT NULL, -- 'multiple_choice', 'true_false', 'code_completion', 'short_answer'
    options JSONB,
    correct_answer JSONB NOT NULL,
    explanation TEXT,
    points INTEGER DEFAULT 1,
    order_index INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_quiz_questions_quiz ON learnflow.quiz_questions(quiz_id);

-- ============================================
-- PROGRESS TRACKING TABLES
-- ============================================

-- Student progress on topics
CREATE TABLE learnflow.student_topic_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID NOT NULL REFERENCES learnflow.users(id) ON DELETE CASCADE,
    topic_id UUID NOT NULL REFERENCES learnflow.topics(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'not_started', -- 'not_started', 'in_progress', 'completed', 'mastered'
    mastery_score DECIMAL(5,2) DEFAULT 0.00, -- 0-100
    time_spent_minutes INTEGER DEFAULT 0,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    last_accessed_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(student_id, topic_id)
);

CREATE INDEX idx_student_topic_progress_student ON learnflow.student_topic_progress(student_id);
CREATE INDEX idx_student_topic_progress_topic ON learnflow.student_topic_progress(topic_id);
CREATE INDEX idx_student_topic_progress_status ON learnflow.student_topic_progress(status);

-- Lesson progress
CREATE TABLE learnflow.student_lesson_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID NOT NULL REFERENCES learnflow.users(id) ON DELETE CASCADE,
    lesson_id UUID NOT NULL REFERENCES learnflow.lessons(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'not_started',
    time_spent_minutes INTEGER DEFAULT 0,
    completed_at TIMESTAMPTZ,
    last_accessed_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(student_id, lesson_id)
);

CREATE INDEX idx_student_lesson_progress_student ON learnflow.student_lesson_progress(student_id);
CREATE INDEX idx_student_lesson_progress_lesson ON learnflow.student_lesson_progress(lesson_id);

-- Exercise submissions
CREATE TABLE learnflow.exercise_submissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID NOT NULL REFERENCES learnflow.users(id) ON DELETE CASCADE,
    exercise_id UUID NOT NULL REFERENCES learnflow.exercises(id) ON DELETE CASCADE,
    submitted_code TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending', -- 'pending', 'running', 'passed', 'failed', 'error'
    test_results JSONB,
    execution_time_ms INTEGER,
    memory_used_mb INTEGER,
    error_message TEXT,
    attempt_number INTEGER DEFAULT 1,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    graded_at TIMESTAMPTZ,
    graded_by UUID REFERENCES learnflow.users(id)
);

CREATE INDEX idx_exercise_submissions_student ON learnflow.exercise_submissions(student_id);
CREATE INDEX idx_exercise_submissions_exercise ON learnflow.exercise_submissions(exercise_id);
CREATE INDEX idx_exercise_submissions_status ON learnflow.exercise_submissions(status);
CREATE INDEX idx_exercise_submissions_submitted ON learnflow.exercise_submissions(submitted_at);

-- Quiz attempts
CREATE TABLE learnflow.quiz_attempts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID NOT NULL REFERENCES learnflow.users(id) ON DELETE CASCADE,
    quiz_id UUID NOT NULL REFERENCES learnflow.quizzes(id) ON DELETE CASCADE,
    score DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    max_score DECIMAL(5,2) NOT NULL,
    passed BOOLEAN DEFAULT false,
    answers JSONB NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    time_spent_seconds INTEGER
);

CREATE INDEX idx_quiz_attempts_student ON learnflow.quiz_attempts(student_id);
CREATE INDEX idx_quiz_attempts_quiz ON learnflow.quiz_attempts(quiz_id);

-- Topic mastery (aggregated)
CREATE TABLE learnflow.topic_mastery (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID NOT NULL REFERENCES learnflow.users(id) ON DELETE CASCADE,
    topic_id UUID NOT NULL REFERENCES learnflow.topics(id) ON DELETE CASCADE,
    mastery_level VARCHAR(20) NOT NULL DEFAULT 'beginner', -- 'beginner', 'learning', 'proficient', 'mastered'
    mastery_score DECIMAL(5,2) DEFAULT 0.00, -- 0-100
    exercise_completion_rate DECIMAL(5,2) DEFAULT 0.00,
    quiz_average_score DECIMAL(5,2) DEFAULT 0.00,
    code_quality_score DECIMAL(5,2) DEFAULT 0.00,
    consistency_streak_days INTEGER DEFAULT 0,
    last_calculated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(student_id, topic_id)
);

CREATE INDEX idx_topic_mastery_student ON learnflow.topic_mastery(student_id);
CREATE INDEX idx_topic_mastery_topic ON learnflow.topic_mastery(topic_id);
CREATE INDEX idx_topic_mastery_level ON learnflow.topic_mastery(mastery_level);

-- ============================================
-- STRUGGLE DETECTION
-- ============================================

CREATE TABLE learnflow.struggle_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID NOT NULL REFERENCES learnflow.users(id) ON DELETE CASCADE,
    teacher_id UUID REFERENCES learnflow.users(id) ON DELETE SET NULL,
    alert_type VARCHAR(50) NOT NULL, -- 'repeated_errors', 'stuck_exercise', 'low_quiz_score', 'inactivity', 'explicit_request'
    severity VARCHAR(20) NOT NULL DEFAULT 'medium', -- 'low', 'medium', 'high', 'critical'
    title VARCHAR(255) NOT NULL,
    description TEXT,
    context JSONB, -- {exercise_id, error_type, count, etc.}
    status VARCHAR(20) NOT NULL DEFAULT 'open', -- 'open', 'acknowledged', 'resolved', 'dismissed'
    acknowledged_at TIMESTAMPTZ,
    acknowledged_by UUID REFERENCES learnflow.users(id),
    resolved_at TIMESTAMPTZ,
    resolved_by UUID REFERENCES learnflow.users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_struggle_alerts_student ON learnflow.struggle_alerts(student_id);
CREATE INDEX idx_struggle_alerts_teacher ON learnflow.struggle_alerts(teacher_id);
CREATE INDEX idx_struggle_alerts_status ON learnflow.struggle_alerts(status);
CREATE INDEX idx_struggle_alerts_created ON learnflow.struggle_alerts(created_at);

-- ============================================
-- ANALYTICS TABLES
-- ============================================

CREATE TABLE analytics.daily_student_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID NOT NULL REFERENCES learnflow.users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    active_minutes INTEGER DEFAULT 0,
    exercises_completed INTEGER DEFAULT 0,
    exercises_attempted INTEGER DEFAULT 0,
    quizzes_taken INTEGER DEFAULT 0,
    avg_quiz_score DECIMAL(5,2) DEFAULT 0.00,
    code_executions INTEGER DEFAULT 0,
    avg_code_quality DECIMAL(5,2),
    topics_studied INTEGER DEFAULT 0,
    lessons_completed INTEGER DEFAULT 0,
    struggle_alerts INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(student_id, date)
);

CREATE INDEX idx_daily_metrics_student ON analytics.daily_student_metrics(student_id);
CREATE INDEX idx_daily_metrics_date ON analytics.daily_student_metrics(date);

CREATE TABLE analytics.class_daily_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    class_id UUID NOT NULL REFERENCES learnflow.classes(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    active_students INTEGER DEFAULT 0,
    total_active_minutes INTEGER DEFAULT 0,
    exercises_completed INTEGER DEFAULT 0,
    avg_mastery_score DECIMAL(5,2),
    struggle_alerts INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(class_id, date)
);

CREATE INDEX idx_class_metrics_class ON analytics.class_daily_metrics(class_id);
CREATE INDEX idx_class_metrics_date ON analytics.class_daily_metrics(date);

-- ============================================
-- AUDIT TABLES
-- ============================================

CREATE TABLE audit.activity_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES learnflow.users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_activity_log_user ON audit.activity_log(user_id);
CREATE INDEX idx_activity_log_resource ON audit.activity_log(resource_type, resource_id);
CREATE INDEX idx_activity_log_created ON audit.activity_log(created_at);

-- ============================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================

ALTER TABLE learnflow.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE learnflow.classes ENABLE ROW LEVEL SECURITY;
CREATE POLICY users_self ON learnflow.users FOR ALL USING (id = current_user_id());
CREATE POLICY classes_teacher ON learnflow.classes FOR ALL USING (teacher_id = current_teacher_id());
CREATE POLICY enrollments_student ON learnflow.class_enrollments FOR ALL USING (student_id = current_user_id());

-- ============================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply to all tables with updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON learnflow.users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_classes_updated_at BEFORE UPDATE ON learnflow.classes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_topics_updated_at BEFORE UPDATE ON learnflow.topics FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_lessons_updated_at BEFORE UPDATE ON learnflow.lessons FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_exercises_updated_at BEFORE UPDATE ON learnflow.exercises FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_struggle_alerts_updated_at BEFORE UPDATE ON learnflow.struggle_alerts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_topic_mastery_updated_at BEFORE UPDATE ON learnflow.topic_mastery FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- VIEWS FOR COMMON QUERIES
-- ============================================

-- Student dashboard view
CREATE VIEW learnflow.student_dashboard AS
SELECT 
    u.id as student_id,
    u.full_name,
    u.email,
    COUNT(DISTINCT ce.class_id) as enrolled_classes,
    COUNT(DISTINCT stp.topic_id) FILTER (WHERE stp.status = 'completed') as topics_completed,
    COUNT(DISTINCT stp.topic_id) FILTER (WHERE stp.status = 'mastered') as topics_mastered,
    AVG(tm.mastery_score) as avg_mastery_score,
    MAX(stp.last_accessed_at) as last_activity,
    COALESCE(SUM(slp.time_spent_minutes), 0) as total_study_minutes
FROM learnflow.users u
LEFT JOIN learnflow.class_enrollments ce ON u.id = ce.student_id AND ce.is_active
LEFT JOIN learnflow.student_topic_progress stp ON u.id = stp.student_id
LEFT JOIN learnflow.topic_mastery tm ON u.id = tm.student_id
LEFT JOIN learnflow.student_lesson_progress slp ON u.id = slp.student_id
WHERE u.role = 'student' AND u.is_active
GROUP BY u.id, u.full_name, u.email;

-- Teacher class overview
CREATE VIEW learnflow.teacher_class_overview AS
SELECT 
    c.id as class_id,
    c.name as class_name,
    c.subject,
    c.grade_level,
    c.is_active,
    COUNT(DISTINCT ce.student_id) as enrolled_students,
    COUNT(DISTINCT ce.student_id) FILTER (WHERE ce.is_active) as active_students,
    AVG(tm.mastery_score) as avg_class_mastery,
    COUNT(sa.id) FILTER (WHERE sa.status = 'open') as open_struggle_alerts,
    MAX(dm.date) as last_activity_date
FROM learnflow.classes c
LEFT JOIN learnflow.class_enrollments ce ON c.id = ce.class_id
LEFT JOIN learnflow.topic_mastery tm ON tm.student_id = ce.student_id
LEFT JOIN learnflow.struggle_alerts sa ON sa.student_id = ce.student_id AND sa.status = 'open'
LEFT JOIN analytics.daily_student_metrics dm ON dm.student_id = ce.student_id
WHERE c.teacher_id = current_teacher_id()
GROUP BY c.id, c.name, c.subject, c.grade_level, c.is_active;

-- ============================================
-- FUNCTIONS
-- ============================================

-- Get current user ID (for RLS)
CREATE OR REPLACE FUNCTION current_user_id() RETURNS UUID AS $$
BEGIN
    RETURN current_setting('app.current_user_id', true)::UUID;
EXCEPTION WHEN OTHERS THEN
    RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Get current teacher ID (for RLS)
CREATE OR REPLACE FUNCTION current_teacher_id() RETURNS UUID AS $$
BEGIN
    RETURN current_setting('app.current_teacher_id', true)::UUID;
EXCEPTION WHEN OTHERS THEN
    RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Calculate topic mastery for a student
CREATE OR REPLACE FUNCTION calculate_topic_mastery(p_student_id UUID, p_topic_id UUID)
RETURNS VOID AS $$
DECLARE
    v_exercise_completion DECIMAL(5,2);
    v_quiz_avg DECIMAL(5,2);
    v_code_quality DECIMAL(5,2);
    v_consistency INTEGER;
    v_mastery_score DECIMAL(5,2);
    v_mastery_level VARCHAR(20);
BEGIN
    -- Exercise completion rate
    SELECT COALESCE(
        COUNT(*) FILTER (WHERE status = 'passed') * 100.0 / NULLIF(COUNT(*), 0),
        0
    ) INTO v_exercise_completion
    FROM learnflow.exercise_submissions es
    JOIN learnflow.exercises e ON es.exercise_id = e.id
    WHERE es.student_id = p_student_id AND e.lesson_id IN (
        SELECT id FROM learnflow.lessons WHERE topic_id = p_topic_id
    );

    -- Quiz average
    SELECT COALESCE(AVG(score), 0) INTO v_quiz_avg
    FROM learnflow.quiz_attempts qa
    JOIN learnflow.quizzes q ON qa.quiz_id = q.id
    JOIN learnflow.lessons l ON q.lesson_id = l.id
    WHERE qa.student_id = p_student_id AND l.topic_id = p_topic_id;

    -- Code quality (placeholder - would analyze submitted code)
    SELECT COALESCE(AVG(code_quality_score), 70) INTO v_code_quality
    FROM analytics.code_quality_metrics
    WHERE student_id = p_student_id AND topic_id = p_topic_id;

    -- Consistency streak (days with activity in last 30 days)
    SELECT COUNT(DISTINCT date) INTO v_consistency
    FROM analytics.daily_student_metrics
    WHERE student_id = p_student_id 
    AND date >= CURRENT_DATE - INTERVAL '30 days'
    AND active_minutes > 0;

    -- Weighted mastery calculation
    v_mastery_score := (
        v_exercise_completion * 0.40 +
        v_quiz_avg * 0.30 +
        v_code_quality * 0.20 +
        LEAST(v_consistency * 100.0 / 30, 100) * 0.10
    );

    -- Determine mastery level
    IF v_mastery_score >= 90 THEN v_mastery_level := 'mastered';
    ELSIF v_mastery_score >= 70 THEN v_mastery_level := 'proficient';
    ELSIF v_mastery_score >= 40 THEN v_mastery_level := 'learning';
    ELSE v_mastery_level := 'beginner';
    END IF;

    -- Upsert mastery record
    INSERT INTO learnflow.topic_mastery (student_id, topic_id, mastery_level, mastery_score, 
        exercise_completion_rate, quiz_average_score, code_quality_score, consistency_streak_days, last_calculated_at)
    VALUES (p_student_id, p_topic_id, v_mastery_level, v_mastery_score,
        v_exercise_completion, v_quiz_avg, v_code_quality, v_consistency, NOW())
    ON CONFLICT (student_id, topic_id) DO UPDATE SET
        mastery_level = EXCLUDED.mastery_level,
        mastery_score = EXCLUDED.mastery_score,
        exercise_completion_rate = EXCLUDED.exercise_completion_rate,
        quiz_average_score = EXCLUDED.quiz_average_score,
        code_quality_score = EXCLUDED.code_quality_score,
        consistency_streak_days = EXCLUDED.consistency_streak_days,
        last_calculated_at = EXCLUDED.last_calculated_at,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- Check for struggle patterns
CREATE OR REPLACE FUNCTION detect_struggle_patterns(p_student_id UUID)
RETURNS VOID AS $$
DECLARE
    r RECORD;
BEGIN
    -- Pattern 1: Same error 3+ times in last hour
    FOR r IN 
        SELECT es.exercise_id, es.error_message, COUNT(*) as error_count
        FROM learnflow.exercise_submissions es
        WHERE es.student_id = p_student_id 
        AND es.status IN ('failed', 'error')
        AND es.submitted_at > NOW() - INTERVAL '1 hour'
        GROUP BY es.exercise_id, es.error_message
        HAVING COUNT(*) >= 3
    LOOP
        INSERT INTO learnflow.struggle_alerts (student_id, alert_type, severity, title, description, context)
        VALUES (p_student_id, 'repeated_errors', 'high',
            'Repeated errors on exercise',
            'Student encountered same error ' || r.error_count || ' times',
            jsonb_build_object('exercise_id', r.exercise_id, 'error_message', r.error_message, 'count', r.error_count))
        ON CONFLICT DO NOTHING;
    END LOOP;

    -- Pattern 2: Stuck on exercise > 10 minutes
    FOR r IN
        SELECT es.exercise_id, MIN(es.submitted_at) as first_attempt, COUNT(*) as attempts
        FROM learnflow.exercise_submissions es
        WHERE es.student_id = p_student_id
        AND es.status IN ('failed', 'error', 'running')
        AND es.submitted_at > NOW() - INTERVAL '10 minutes'
        GROUP BY es.exercise_id
        HAVING COUNT(*) >= 5
    LOOP
        INSERT INTO learnflow.struggle_alerts (student_id, alert_type, severity, title, description, context)
        VALUES (p_student_id, 'stuck_exercise', 'medium',
            'Stuck on exercise for extended time',
            'Student has attempted exercise ' || r.attempts || ' times in 10 minutes',
            jsonb_build_object('exercise_id', r.exercise_id, 'attempts', r.attempts))
        ON CONFLICT DO NOTHING;
    END LOOP;

    -- Pattern 3: Quiz score < 50%
    FOR r IN
        SELECT qa.quiz_id, qa.score
        FROM learnflow.quiz_attempts qa
        WHERE qa.student_id = p_student_id
        AND qa.completed_at > NOW() - INTERVAL '1 hour'
        AND qa.score < 50
    LOOP
        INSERT INTO learnflow.struggle_alerts (student_id, alert_type, severity, title, description, context)
        VALUES (p_student_id, 'low_quiz_score', 'medium',
            'Low quiz score detected',
            'Student scored ' || r.score || '% on quiz',
            jsonb_build_object('quiz_id', r.quiz_id, 'score', r.score))
        ON CONFLICT DO NOTHING;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions
GRANT USAGE ON SCHEMA learnflow TO learnflow_app;
GRANT USAGE ON SCHEMA analytics TO learnflow_app;
GRANT USAGE ON SCHEMA audit TO learnflow_app;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA learnflow TO learnflow_app;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA analytics TO learnflow_app;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA audit TO learnflow_app;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA learnflow TO learnflow_app;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA analytics TO learnflow_app;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA learnflow TO learnflow_app;
