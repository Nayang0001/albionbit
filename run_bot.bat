@echo off
REM Albion Party Manager - start bot
SETLOCAL

REM Prefer .venv if it exists otherwise fall back to venv
IF EXIST "%~dp0.venv\Scripts\Activate.bat" (
    CALL "%~dp0.venv\Scripts\Activate.bat"
) ELSE IF EXIST "%~dp0venv\Scripts\Activate.bat" (
    CALL "%~dp0venv\Scripts\Activate.bat"
) ELSE (
    echo No se encontró el entorno virtual .venv ni venv en este proyecto.
    pause
    EXIT /B 1
)

cd /d "%~dp0"
python main.py
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo El bot salió con código de error %ERRORLEVEL%.
)
pause