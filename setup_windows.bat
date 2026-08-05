@echo off
setlocal
cd /d "%~dp0"
echo Instalando dependencias de StatLab...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo La instalacion no termino correctamente.
  echo Verifique que Python 3.11 o superior este instalado y agregado al PATH.
  pause
  exit /b 1
)
echo.
echo Instalacion completada. Ejecute run_demo.bat para probar el sistema.
pause
