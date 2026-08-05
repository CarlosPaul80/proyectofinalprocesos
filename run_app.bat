@echo off
setlocal
cd /d "%~dp0"
python main.py
if errorlevel 1 (
  echo.
  echo No se pudo iniciar StatLab. Instale las dependencias con:
  echo python -m pip install -r requirements.txt
  pause
)
