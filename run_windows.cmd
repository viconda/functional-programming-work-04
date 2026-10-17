@echo off
chcp 65001 >nul
cd /d "%~dp0"
py -3 -c "import sys; sys.exit(sys.version_info < (3,12))" >nul 2>&1
if not errorlevel 1 (
    py -3 run_all.py
    goto done
)
python -c "import sys; sys.exit(sys.version_info < (3,12))" >nul 2>&1
if not errorlevel 1 (
    python run_all.py
    goto done
)
set "TASK_PYTHON=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if exist "%TASK_PYTHON%" (
    "%TASK_PYTHON%" run_all.py
) else (
    echo Please install Python 3.12 or newer, then run this file again.
)
:done
pause
