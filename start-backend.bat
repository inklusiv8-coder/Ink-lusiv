@echo off
cd /d "%~dp0"
set SUPABASE_URL=https://tkjwwtwtjatcbdxvwwzu.supabase.co
REM Replace with your Supabase service role key for server-side inserts
set SUPABASE_SERVICE_ROLE_KEY=
REM Optional: set your public anon key for readonly access only
set SUPABASE_KEY=
py -m pip install -r requirements.txt
py server.py
pause
