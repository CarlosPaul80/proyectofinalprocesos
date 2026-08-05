@echo off
setlocal
cd /d "%~dp0"
python -m PyInstaller --noconfirm --clean --windowed --name StatLab ^
  --add-data "data;data" ^
  --collect-all matplotlib ^
  --collect-all openpyxl ^
  --collect-all customtkinter ^
  main.py
if errorlevel 1 (
  echo No se pudo construir el ejecutable.
  pause
  exit /b 1
)
echo.
echo Ejecutable generado en dist\StatLab\StatLab.exe
pause
