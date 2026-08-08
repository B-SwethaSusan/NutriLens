CREATE EXTENSION IF NOT EXISTS vector;

-- The application creates tables through SQLAlchemy on startup.
-- This migration is intentionally safe to re-run and is also suitable for a
-- Supabase SQL editor after the first application boot.
