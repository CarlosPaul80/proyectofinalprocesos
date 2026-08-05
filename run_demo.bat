@echo off
setlocal
cd /d "%~dp0"
python main.py --demo
if errorlevel 1 pause
