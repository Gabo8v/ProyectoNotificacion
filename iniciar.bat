@echo off
title Sistema de Notificaciones
cd /d "%~dp0"

echo ============================================
echo  Sistema de Gestion de Notificaciones
echo ============================================
echo.

REM ---- 1. Activar entorno virtual ----
if not exist ".venv\Scripts\activate" (
    echo [ERROR] No se encuentra .venv\Scripts\activate
    echo Ejecuta: python -m venv .venv
    pause
    exit /b 1
)
echo [1/4] Activando entorno virtual...
call .venv\Scripts\activate

REM ---- 2. Verificar Docker e iniciar contenedores ----
echo [2/4] Verificando Docker...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker no esta corriendo. Abri Docker Desktop primero.
    pause
    exit /b 1
)

docker ps --format "{{.Names}}" | findstr "notificaciones-db" >nul
if %errorlevel% neq 0 (
    echo       Iniciando PostgreSQL y pgAdmin...
    docker-compose up -d
) else (
    echo       PostgreSQL y pgAdmin ya estan corriendo.
)

REM ---- 3. Iniciar WhatsApp bot ----
echo [3/4] Iniciando WhatsApp bot...
tasklist /fi "WindowTitle eq WhatsApp Bot*" 2>nul | findstr "node.exe" >nul
if %errorlevel% neq 0 (
    start "WhatsApp Bot" /min cmd /c "cd /d whatsapp-bot && node index.js"
    echo       WhatsApp bot iniciado (ventana minimizada).
    echo       Si es la primera vez, escanea el QR que aparecera.
) else (
    echo       WhatsApp bot ya esta corriendo.
)

REM ---- 4. Iniciar FastAPI ----
echo [4/4] Iniciando FastAPI...
echo.
echo ============================================
echo  Dashboard: http://localhost:8000/dashboard/
echo  API Docs:  http://localhost:8000/docs
echo  Health:    http://localhost:8000/health
echo ============================================
echo.
echo  Presiona Ctrl+C para detener el servidor
echo.

start http://localhost:8000/dashboard/
.venv\Scripts\uvicorn app.main:app --reload --port 8000

pause
