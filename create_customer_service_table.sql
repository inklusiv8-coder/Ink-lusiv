-- Create customer_service table for WhatsApp messages
CREATE TABLE IF NOT EXISTS public.customer_service (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255),
  phone VARCHAR(20),
  whatsapp VARCHAR(20) DEFAULT '9138154963',
  message TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_customer_service_email ON public.customer_service(email);
CREATE INDEX IF NOT EXISTS idx_customer_service_phone ON public.customer_service(phone);
CREATE INDEX IF NOT EXISTS idx_customer_service_created_at ON public.customer_service(created_at);

-- Set up Row Level Security (RLS)
ALTER TABLE public.customer_service ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Allow insert" ON public.customer_service;
DROP POLICY IF EXISTS "Allow select for authenticated" ON public.customer_service;
DROP POLICY IF EXISTS "Allow service role all" ON public.customer_service;

-- Allow anyone to insert (for frontend)
CREATE POLICY "Allow insert" ON public.customer_service
  FOR INSERT
  WITH CHECK (true);

-- Allow authenticated users (admin) to select
CREATE POLICY "Allow select for authenticated" ON public.customer_service
  FOR SELECT
  USING (auth.role() = 'authenticated');

-- Allow service role to do everything
CREATE POLICY "Allow service role all" ON public.customer_service
  USING (true)
  WITH CHECK (true);
