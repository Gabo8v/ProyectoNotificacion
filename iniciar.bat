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
echo [3/4] Verificando WhatsApp bot...
call :iniciar_bot
if %errorlevel% neq 0 (
    echo [ERROR] No se pudo iniciar el WhatsApp bot.
    pause
    exit /b 1
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
exit /b 0

:iniciar_bot
    REM Intentar via pm2 primero
    where pm2 >nul 2>&1
    if %errorlevel% neq 0 (
        goto start_bot_direct
    )

    pm2 list 2>nul | findstr "whatsapp-bot.*online" >nul
    if %errorlevel% equ 0 (
        echo       WhatsApp bot ya esta corriendo (pm2).
        exit /b 0
    )

    echo       Iniciando WhatsApp bot via pm2...
    pm2 start whatsapp-bot 2>nul
    if %errorlevel% equ 0 (
        echo       WhatsApp bot iniciado con pm2.
        echo       Si es la primera vez, escanea el QR con: pm2 logs whatsapp-bot
        exit /b 0
    )
    echo [WARN] pm2 fallo, intentando inicio directo...

:start_bot_direct
    tasklist /fi "WindowTitle eq WhatsApp Bot*" 2>nul | findstr "node.exe" >nul
    if %errorlevel% neq 0 (
        start "WhatsApp Bot" /min cmd /c "cd /d whatsapp-bot && node index.js"
        echo       WhatsApp bot iniciado (ventana minimizada).
        echo       Si es la primera vez, escanea el QR que aparecera.
        exit /b 0
    ) else (
        echo       WhatsApp bot ya esta corriendo.
        exit /b 0
    )
