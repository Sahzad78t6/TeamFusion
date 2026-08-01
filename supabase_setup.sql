-- Create the users table
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    refresh_token TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Enable Row Level Security (RLS)
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if any to avoid conflicts
DROP POLICY IF EXISTS "Allow anonymous insert" ON public.users;
DROP POLICY IF EXISTS "Allow anonymous select" ON public.users;
DROP POLICY IF EXISTS "Allow anonymous update" ON public.users;

-- Create policies to allow the API to function
-- In a production environment, you should use service_role key to bypass RLS
-- However, since the current code uses the anon key, we must allow access

-- Allow insertions (Signup)
CREATE POLICY "Allow anonymous insert" 
ON public.users 
FOR INSERT 
TO anon 
WITH CHECK (true);

-- Allow reading users (Login, duplicate email check)
CREATE POLICY "Allow anonymous select" 
ON public.users 
FOR SELECT 
TO anon 
USING (true);

-- Allow updating users (Updating refresh token on Login/Logout)
CREATE POLICY "Allow anonymous update" 
ON public.users 
FOR UPDATE 
TO anon 
USING (true) 
WITH CHECK (true);
