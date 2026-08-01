-- ==========================================
-- GrowthOS Supabase Database Schema
-- ==========================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ------------------------------------------
-- 1. Profiles Table (Extends auth.users)
-- ------------------------------------------
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    bio TEXT,
    timezone TEXT DEFAULT 'UTC',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ------------------------------------------
-- 2. Identity Twin Table
-- ------------------------------------------
CREATE TABLE IF NOT EXISTS public.identity_twin (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE,
    core_values JSONB DEFAULT '[]'::jsonb,
    strengths JSONB DEFAULT '[]'::jsonb,
    growth_areas JSONB DEFAULT '[]'::jsonb,
    identity_vector JSONB DEFAULT '{}'::jsonb,
    archetype TEXT,
    drift_score DOUBLE PRECISION DEFAULT 0.0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ------------------------------------------
-- 3. Aspirations Table
-- ------------------------------------------
CREATE TABLE IF NOT EXISTS public.aspirations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT DEFAULT 'general',
    target_date DATE,
    status TEXT DEFAULT 'active',
    priority INT DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ------------------------------------------
-- 4. Habits Table
-- ------------------------------------------
CREATE TABLE IF NOT EXISTS public.habits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    aspiration_id UUID REFERENCES public.aspirations(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    description TEXT,
    frequency TEXT DEFAULT 'daily',
    target_count INT DEFAULT 1,
    current_streak INT DEFAULT 0,
    best_streak INT DEFAULT 0,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ------------------------------------------
-- 5. Recommendations Table
-- ------------------------------------------
CREATE TABLE IF NOT EXISTS public.recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    type TEXT DEFAULT 'general',
    reasoning TEXT,
    source TEXT DEFAULT 'ai_curator',
    is_read BOOLEAN DEFAULT FALSE,
    is_applied BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ------------------------------------------
-- 6. Reflections Table
-- ------------------------------------------
CREATE TABLE IF NOT EXISTS public.reflections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    prompt TEXT,
    entry TEXT NOT NULL,
    sentiment_score DOUBLE PRECISION,
    key_insights JSONB DEFAULT '[]'::jsonb,
    mood TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ------------------------------------------
-- 7. Analytics Table
-- ------------------------------------------
CREATE TABLE IF NOT EXISTS public.analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    metric_name TEXT NOT NULL,
    metric_value NUMERIC NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

-- ------------------------------------------
-- 8. ML Predictions Table
-- ------------------------------------------
CREATE TABLE IF NOT EXISTS public.ml_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    model_name TEXT NOT NULL,
    prediction JSONB NOT NULL,
    confidence DOUBLE PRECISION,
    features_used JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ------------------------------------------
-- 9. Notifications Table
-- ------------------------------------------
CREATE TABLE IF NOT EXISTS public.notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    type TEXT DEFAULT 'info',
    is_read BOOLEAN DEFAULT FALSE,
    action_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ------------------------------------------
-- Indexes for Performance
-- ------------------------------------------
CREATE INDEX IF NOT EXISTS idx_aspirations_user_id ON public.aspirations(user_id);
CREATE INDEX IF NOT EXISTS idx_habits_user_id ON public.habits(user_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_user_id ON public.recommendations(user_id);
CREATE INDEX IF NOT EXISTS idx_reflections_user_id ON public.reflections(user_id);
CREATE INDEX IF NOT EXISTS idx_analytics_user_id ON public.analytics(user_id);
CREATE INDEX IF NOT EXISTS idx_ml_predictions_user_id ON public.ml_predictions(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON public.notifications(user_id);

-- ------------------------------------------
-- Row Level Security (RLS) Policies
-- ------------------------------------------
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.identity_twin ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.aspirations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.habits ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reflections ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ml_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;

-- Base RLS Policy per table (Users can access their own data)
CREATE POLICY "Users access own profile" ON public.profiles FOR ALL USING (auth.uid() = id);
CREATE POLICY "Users access own identity_twin" ON public.identity_twin FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users access own aspirations" ON public.aspirations FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users access own habits" ON public.habits FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users access own recommendations" ON public.recommendations FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users access own reflections" ON public.reflections FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users access own analytics" ON public.analytics FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users access own ml_predictions" ON public.ml_predictions FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users access own notifications" ON public.notifications FOR ALL USING (auth.uid() = user_id);
