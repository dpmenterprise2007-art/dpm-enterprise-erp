@echo off
title DPM ENTERPRISE ERP
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  py -3 -m venv .venv
  if errorlevel 1 goto error
)
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r backend\requirements.txt
if errorlevel 1 goto error
".venv\Scripts\python.exe" start_dpm_erp.py
goto end
:error
echo Setup failed. Check Python installation and messages above.
pause
:end
