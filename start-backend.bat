@echo off
cd /d "%~dp0"
set SUPABASE_URL=https://tkjwwtwtjatcbdxvwwzu.supabase.co
REM If you want to override .env, set these here. Otherwise leave blank to use .env values.
REM set SUPABASE_SERVICE_ROLE_KEY=
REM set SUPABASE_KEY=
py -m pip install -r requirements.txt
py server.py
pause
