-- Migration: Add missing columns to users table
-- This fixes the schema cache errors when syncing user data to Supabase

ALTER TABLE users ADD COLUMN IF NOT EXISTS "fullName" TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS "phoneNumber" TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS "address" TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS "city" TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS "zipCode" TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS "createdAt" TIMESTAMP WITH TIME ZONE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS "email" TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS "id" UUID;