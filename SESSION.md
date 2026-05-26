# SESSION LOG - Sistema de Gestion de Notificaciones

## Informacion General

- **Proyecto:** Sistema de Gestion de Notificaciones
- **Stack:** Python (FastAPI) + PostgreSQL (Docker) + whatsapp-web.js (Node.js)
- **Version de Python:** 3.12
- **Version de Node.js:** 24.16.0
- **Version de npm:** 11.13.0
- **Version de Docker:** 29.4.1
- **Repo:** https://github.com/Gabo8v/ProyectoNotificacion
- **Colaboradores:** Gabo8v (vos), luismateocasamayor (Mateo)
- **Drive Compartido:** https://drive.google.com/drive/folders/10HiQXXMJdisKhBasPi_aKHzJpwqHe1ur
- **Plan docx original:** https://docs.google.com/document/d/1eW6cN1FZ1_B7Hy2o5GxW77qw3lmdQxIs/edit?usp=drivesdk&ouid=108954821762539778822&rtpof=true&sd=true

---

## ESTADO AL CIERRE DE SESION (22/05/2026)

### Servicios activos al cerrar:
| Servicio | Puerto | Estado |
|----------|--------|--------|
| FastAPI (uvicorn) | 8000 | ✅ CORRIENDO |
| PostgreSQL (Docker) | 5432 | ✅ CORRIENDO (docker) |
| pgAdmin (Docker) | 5050 | ✅ CORRIENDO (docker) |
| WhatsApp Bot (Node.js) | 3001 | ✅ CORRIENDO |

### Para reanudar la sesion:
```powershell
# Activar entorno
cd C:\Users\Gabo8\OneDrive\Escritorio\ProyectoNotificacion
.venv\Scripts\activate

# Verificar que todos los servicios esten arriba
docker ps | findstr notificaciones     # Deben aparecer notificaciones-db y notificaciones-pgadmin
pm2 status                              # whatsapp-bot debe estar online
curl.exe -s http://localhost:8000/health  # FastAPI

# Si falta alguno, iniciar:
docker-compose up -d                           # PostgreSQL + pgAdmin
pm2 start whatsapp-bot                         # WhatsApp (desde el proyecto)
.venv\Scripts\uvicorn app.main:app --reload --port 8000  # FastAPI
```

### Archivos sensibles que NO estan en Git (deben copiarse manualmente al clonar):
- `credentials.json` (Gmail OAuth client ID/secret)
- `gmail_token.pickle` (Gmail OAuth token)
- `.env` (DATABASE_URL y configs)
- `whatsapp-bot/.wwebjs_auth/` (sesion de WhatsApp escaneada)

---

## FASE 1 - Setup del Proyecto ✅ (COMPLETADA)

### Archivos del proyecto
| Archivo | Proposito |
|---------|-----------|
| `app/__init__.py` | Package init |
| `app/main.py` | Entry point FastAPI (importa routers) |
| `app/config.py` | Settings via pydantic-settings (lee .env) |
| `app/database.py` | SQLAlchemy engine + SessionLocal + get_db() + Base |
| `app/models/__init__.py` | Re-exporta User, Notification, Template, Log |
| `app/models/user.py` | User (id UUID, name, email, phone, is_active, timestamps) |
| `app/models/notification.py` | Notification (id UUID, user_id FK, channel enum, status enum, subject, body, external_id, conversation_ref, error_message, timestamps) |
| `app/models/template.py` | Template (id UUID, name unique, keywords CSV, subject, body, is_active, timestamps) |
| `app/models/log.py` | Log (id UUID, channel nullable, level enum info/warning/error, message, details, timestamp) |
| `app/routers/health.py` | GET /health -> {"status":"ok","service":"notificaciones"} |
| `app/routers/notifications.py` | POST /notifications/send, GET /notifications/history |
| `app/routers/templates.py` | GET /templates/, POST /templates/, DELETE /templates/{id} |
| `app/routers/whatsapp.py` | POST /whatsapp/webhook (recibe msjs del bot) |
| `app/schemas/notification.py` | NotificationCreate, NotificationOut (Pydantic) |
| `app/schemas/template.py` | TemplateCreate, TemplateOut (Pydantic) |
| `app/services/gmail.py` | GmailService completo (auth, send, read, mark_read) + auth_url() + save_token() auxiliares |
| `app/services/whatsapp.py` | WhatsAppService (send_message con @c.us auto, is_healthy) |
| `app/services/notification_service.py` | NotificationService (send, mark_sent, mark_failed, get_history, log) |
| `whatsapp-bot/index.js` | Servidor Express + whatsapp-web.js client |
| `whatsapp-bot/package.json` | Dependencias Node.js |
| `app/services/integration_service.py` | Orquestador bidireccional Gmail <-> WhatsApp |
| `app/tasks/__init__.py` | Package init |
| `app/tasks/polling.py` | Background task polling de Gmail |
| `app/routers/dashboard.py` | Dashboard web con Jinja2 |
| `app/templates/base.html` | Layout base del dashboard |
| `app/templates/index.html` | Pagina de resumen |
| `app/templates/send.html` | Formulario de envio |
| `app/templates/templates.html` | CRUD de templates |
| `app/templates/history.html` | Historial con filtros |
| `app/static/style.css` | Estilos dark mode |
| `tests/conftest.py` | Fixtures de pytest |
| `tests/test_health.py` | Test health endpoint |
| `tests/test_notifications.py` | Test notificaciones |
| `tests/test_templates.py` | Test templates |
| `tests/test_whatsapp.py` | Test webhook WhatsApp |
| `tests/test_dashboard.py` | Test dashboard |
| `thunder-collection_Notificaciones.json` | Collection Thunder Client |
| `GUIA_DE_USO.md` | Guia paso a paso con ejemplo practico |
| `app/templates/users.html` | Gestion de usuarios desde dashboard |
| `docker-compose.yml` | PostgreSQL 15 + pgAdmin |
| `alembic.ini` | Conexion a DB para migraciones |
| `alembic/env.py` | Importa Base.metadata para autogenerate |
| `alembic/versions/080d0d18ec8d_tablas_iniciales.py` | Migracion con 4 tablas |
| `.env` | DATABASE_URL, rutas credenciales, WHATSAPP_BOT_URL |
| `.env.example` | Template para .env |
| `.gitignore` | Exclusiones: .venv, .env, credenciales, tokens, node_modules, .wwebjs_* |
| `requirements.txt` | fastapi, uvicorn, sqlalchemy, psycopg2-binary, alembic, pydantic-settings, google-api-python-client, google-auth-*, requests, python-docx, pytest, httpx |
| `SESSION.md` | Este archivo |

### Decisiones de arquitectura
- **PostgreSQL** como base de datos (no SQLite) - mas escalable para produccion
- **UUID** como primary keys (no autoincrement) - mejor para distribuido
- **Enums** en DB para channel (email/whatsapp) y status (pending/sent/failed)
- **conversation_ref** para tracking de hilos entre Gmail y WhatsApp
- **pydantic-settings** para config via .env
- **SQLAlchemy 2.0** con Mapped/mapped_column (type annotations)
- **Enum nativos de Python** + SQLAlchemy Enum para consistencia

---

## FASE 2 - Gmail API ✅ (COMPLETADA)

### Configuracion de Google Cloud
- **Proyecto:** mimetic-card-497013-c2
- **API habilitada:** Gmail API
- **Tipo de credencial:** OAuth 2.0 Desktop App
- **Scope:** https://www.googleapis.com/auth/gmail.modify
- **Redirect URI:** http://localhost

### Archivos de Gmail
| Archivo | Ubicacion | Propósito |
|---------|-----------|-----------|
| `credentials.json` | Raiz del proyecto | NO COMMITEAR - Client ID + Secret |
| `gmail_token.pickle` | Raiz del proyecto | NO COMMITEAR - Token OAuth |

### Funciones disponibles en `app.services.gmail`
```python
GmailService()
    .send_email(to: str, subject: str, body: str) -> dict | None
    .read_inbox(max_results: int = 5) -> list[dict]
    .mark_as_read(message_id: str) -> bool
    .is_ready() -> bool

# Funciones auxiliares:
auth_url()                        # Genera URL para autorizar
save_token(code: str)             # Guarda token desde codigo OAuth
get_service() -> Resource | None  # Obtiene servicio Gmail API
```

### Tokens y refresh
- El token se refresca automaticamente via `google.auth.transport.requests.Request`
- Se guarda en `gmail_token.pickle`
- Si expira y no hay refresh_token, pide re-autenticar

---

## FASE 3 - Bot WhatsApp ✅ (COMPLETADA)

### Configuracion whatsapp-web.js
- **Navegador:** Brave (Chromium-based)
- **ExecutablePath:** `C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe`
- **Headless:** true
- **Args:** `--no-sandbox`, `--disable-gpu`
- **Estrategia de auth:** LocalAuth (guarda sesion en `.wwebjs_auth/`)

### Formato de numeros WhatsApp
```
5493875360385@c.us
# 54 = codigo pais Argentina
# 9 = prefijo movil Argentina
# 3875360385 = numero
# @c.us = sufijo para chat individual
```
El servicio `WhatsAppService.send_message()` agrega `@c.us` automaticamente si no lo tiene.

### Endpoints del bot (Express, puerto 3001)
| Metodo | Ruta | Proposito |
|--------|------|-----------|
| POST | `/send-message` | Enviar mensaje `{"to":"...","message":"..."}` |
| GET | `/health` | Health check |

### Comunicacion Python -> Node
FastAPI se comunica con el bot via HTTP local:
- Python usa `WhatsAppService.send_message()` que POSTea a `http://localhost:3001/send-message`
- El bot recibe mensajes y POSTea a `http://localhost:8000/whatsapp/webhook`

### Webhook en FastAPI
`POST /whatsapp/webhook` recibe:
```json
{
  "from": "5493875360385@c.us",
  "body": "mensaje",
  "messageId": "true_xxx@lid_yyy",
  "timestamp": 1234567890
}
```

---

## FASE 4 - Core Notificaciones ✅ (COMPLETADA)

### Servicios Docker corriendo
```yaml
# docker-compose.yml
postgres: puerto 5432, user=user, password=password, db=notificaciones
pgadmin:  puerto 5050, email=admin@notificaciones.com, password=admin
```

### Base de datos - Esquema actual
```sql
users          (id UUID, name, email UNIQUE, phone, is_active, created_at, updated_at)
notifications  (id UUID, user_id FK->users, channel ENUM, status ENUM, subject, body,
                external_id, conversation_ref, error_message, created_at, sent_at)
templates      (id UUID, name UNIQUE, keywords, subject, body, is_active, created_at, updated_at)
logs           (id UUID, channel ENUM nullable, level ENUM, message, details, created_at)
```

### Endpoints REST funcionales
| Metodo | Ruta | Request | Response |
|--------|------|---------|----------|
| GET | `/health` | - | `{"status":"ok","service":"notificaciones"}` |
| POST | `/notifications/send` | `{"channel":"email","subject":"...","body":"..."}` | Notification JSON |
| GET | `/notifications/history?channel=&status=&limit=&offset=` | Query params | `[Notification, ...]` |
| GET | `/templates/` | - | `[Template, ...]` |
| POST | `/templates/` | `{"name":"...","keywords":"...","subject":"...","body":"..."}` | Template JSON |
| DELETE | `/templates/{id}` | Path param UUID | `{"ok":true}` |
| POST | `/whatsapp/webhook` | `{"from":"...","body":"...","messageId":"...","timestamp":...}` | `{"status":"received"}` |

### NotificationService (`app.services.notification_service`)
```python
NotificationService(db)
    .send(data: NotificationCreate) -> Notification
    .mark_sent(notification_id, external_id=None)
    .mark_failed(notification_id, error: str)
    .get_history(channel, status, limit=50, offset=0) -> list[Notification]
    .log(channel, level, message, details=None)
```

---

## FASE 5 - Integracion Bidireccional ✅ (COMPLETADA)

### Resumen de lo implementado

#### 5a. Gmail -> WhatsApp (polling) ✅
- Creado `app/tasks/polling.py` con `poll_gmail()` y `run_polling_loop()`
- Background task via `asyncio` que cada 30s lee inbox de Gmail
- Por cada correo no leido, crea Notification, envía por WhatsApp, marca como leido
- Usa `conversation_ref = "gmail:<email>"` para tracking

#### 5b. WhatsApp -> Gmail (respuesta automatica) ✅
- Webhook `/whatsapp/webhook` modificado para usar `IntegrationService`
- Detecta keywords en el mensaje contra los Templates activos
- Si coincide, envía email automaticamente via GmailService
- Guarda todo en la DB con estado SENT/FAILED

#### 5c. Matching de hilos ✅
- `conversation_ref` formato: `gmail:<from_email>` para entrantes de Gmail
- `NotificationService.find_by_conversation_ref()` para buscar hilos
- `get_user_by_email()` y `get_user_by_phone()` para lookup de usuarios

### Archivos nuevos
- `app/services/integration_service.py` - Orquesta el flujo bidireccional
- `app/tasks/__init__.py` - Package init
- `app/tasks/polling.py` - Background polling loop

### Archivos modificados
- `app/services/notification_service.py` - Metodos de matching
- `app/routers/whatsapp.py` - Webhook con procesamiento de templates
- `app/main.py` - Lifespan handler para arrancar polling

### Flujo completo
```
Gmail (correo nuevo) -> poll_gmail() -> IntegrationService.email_to_whatsapp() -> WhatsApp
WhatsApp (respuesta) -> /whatsapp/webhook -> IntegrationService.whatsapp_to_email() -> Gmail (template match)
```

---

## FASE 6 - Dashboard ✅ (COMPLETADA)

### Resumen de lo implementado

#### Paginas del dashboard
| Ruta | Descripcion |
|------|-------------|
| `GET /dashboard/` | Resumen con tarjetas (total, enviadas, pendientes, fallidas) + ultimas 10 notificaciones |
| `GET /dashboard/send` | Formulario para enviar notificacion manual |
| `POST /dashboard/send` | Procesa el envio |
| `GET /dashboard/templates` | Lista templates + formulario para crear nuevo |
| `POST /dashboard/templates` | Crea nuevo template |
| `POST /dashboard/templates/{id}/delete` | Elimina template |
| `GET /dashboard/history` | Historial con filtros por canal/estado + paginacion |
| `GET /dashboard/users` | Lista usuarios + formulario para crear nuevo |
| `POST /dashboard/users` | Crea nuevo usuario |
| `POST /dashboard/users/{id}/delete` | Elimina usuario |

#### Archivos creados
- `app/routers/dashboard.py` - Router con Jinja2 templates
- `app/templates/base.html` - Layout base con navegacion
- `app/templates/index.html` - Pagina de resumen
- `app/templates/send.html` - Formulario de envio
- `app/templates/templates.html` - CRUD de templates
- `app/templates/history.html` - Historial con filtros y paginacion
- `app/templates/users.html` - Gestion de usuarios
- `app/static/style.css` - Estilos dark mode

#### Archivos modificados
- `app/main.py` - Monta static files e incluye dashboard router

### Notas
- Diseño dark mode con paleta slate/blue
- Los flash messages se pasan por query params en redirects
- Jinja2 ya venia instalado como dependencia de Starlette/FastAPI

---

## FASE 7 - Documentacion y Tests ✅ (COMPLETADA)

### Tests (pytest + httpx)
- `tests/conftest.py` - Fixtures con base de datos PostgreSQL dedicada (`notificaciones_test`)
- `tests/test_health.py` - Health check endpoint
- `tests/test_notifications.py` - CRUD notificaciones (6 tests)
- `tests/test_templates.py` - CRUD templates (5 tests)
- `tests/test_whatsapp.py` - Webhook WhatsApp
- `tests/test_dashboard.py` - Paginas del dashboard (4 tests)
- **Total: 17 tests, todos pasando**

### Documentacion
- `README.md` completo con setup, estructura, endpoints y flujo de integracion
- `thunder-collection_Notificaciones.json` - Collection para Thunder Client / Postman
- `GUIA_DE_USO.md` - Guia paso a paso con ejemplo practico
- `SESSION.md` actualizado con todas las fases

### Extras agregados post-cierre (22/05)
- **Envio real de notificaciones** - `POST /notifications/send` ahora envía realmente por Gmail/WhatsApp según el canal y actualiza status a "sent" o "failed"
- **Gestion de usuarios desde dashboard** (`/dashboard/users`) - CRUD completo sin SQL, con formulario y placeholders claros
- **Seed data**: Admin Desarrollador + Juan Perez precargados en DB (mas tarde se agregaron Gabo, Vale, Mateo con datos reales)
- **Selector de usuario en formulario de envio** - dropdown con nombre+email en lugar de pegar UUID
- **Selector de template** - autocompleta asunto y cuerpo al seleccionar un template
- **Panel de pendientes** en la pagina de enviar (columna derecha) - muestra notificaciones pendientes con un click para responder
- **Metricas en resumen** - ahora muestra también cantidad de usuarios y templates + botones de acceso rapido
- **Nombre de usuario en tablas** - Resumen e Historial muestran el nombre en vez del UUID
- **Limpiar filtros** en Historial
- **Link a API Docs** en la navegacion
- Guia de uso practica (`GUIA_DE_USO.md`)

### Mejoras de UX aplicadas
- Formularios con placeholders mas descriptivos
- Mensajes flash mas claros (ej: "Notificacion enviada para Admin Desarrollador")
- Columnas de detalle en historial (ID externo, errores)
- Navegacion con active states
- Diseño responsive con grid en pagina de envio

---

## Comandos imprescindibles

```powershell
# --- CADA VEZ QUE SE REANUDA LA SESION ---

# Activar entorno virtual
.venv\Scripts\activate

# Iniciar PostgreSQL (si no esta corriendo)
docker-compose up -d

# Iniciar WhatsApp bot (NUEVA TERMINAL, en segundo plano)
cd whatsapp-bot
Start-Process -WindowStyle Hidden -FilePath "node" -ArgumentList "index.js"

# Iniciar FastAPI
.venv\Scripts\uvicorn app.main:app --reload --port 8000

# --- COMANDOS UTILES ---

# Ver logs de PostgreSQL
docker logs notificaciones-db

# Ejecutar migracion nueva
.venv\Scripts\alembic revision --autogenerate -m "descripcion"
.venv\Scripts\alembic upgrade head

# Ver tablas en PostgreSQL
docker exec -it notificaciones-db psql -U user -d notificaciones -c "\dt"

# Probar API
curl -s http://localhost:8000/health

# Probar envio WhatsApp
curl -s -X POST http://localhost:3001/send-message -H "Content-Type: application/json" -d '{"to":"5493875360385@c.us","message":"Hola"}'

# Hacer commit y push
git add -A
git commit -m "mensaje"
git push

# Subir SESSION.md actualizado a Drive
python C:\Users\Gabo8\OneDrive\Escritorio\InicioOpenCode\scripts\drive_upload.py SESSION.md --folder "Notificaciones-Credenciales"
```

---

## Notas importantes para el AI al reanudar

1. **Primera accion al reanudar:** Leer este archivo SESSION.md completo.
2. **Los servicios Docker pueden estar caidos** (PostgreSQL, pgAdmin) - levantarlos con `docker-compose up -d`.
3. **El bot de WhatsApp puede estar caido** - la sesion LocalAuth persiste, solo hay que reiniciar el proceso Node.js.
4. **FastAPI puede estar caido** - reiniciar con uvicorn.
5. **Puerto 8000 puede estar ocupado** por otro container viejo (`prueba_djangoISDM`) - detenerlo con `docker stop prueba_djangoISDM`.
6. **El AI puede modificar este archivo** al completar nuevas fases para mantener el estado actualizado.
7. **Despues de modificar SESSION.md**, siempre hacer commit+push y subir a Drive.

### Flujo de polling
- Se activa automaticamente al iniciar FastAPI (lifespan handler)
- Intervalo: 30 segundos
- Si Gmail no tiene token, logea warning y no falla

### Decisiones de codigo que debe respetar el AI
- Usar `Mapped[mapped_column()]` de SQLAlchemy 2.0
- UUID como tipo de dato para IDs
- Enums de Python para channel/status/level
- FastAPI con dependencia `Depends(get_db)` para sesiones de DB
- Los servicios (gmail, whatsapp, notification) son clases, no funciones sueltas
- El bot de WhatsApp se comunica por HTTP (no por libreria directa)
- No instalar nuevas dependencias sin preguntar si son pesadas (>20MB)

---

## Links rapidos

- **Drive compartido:** https://drive.google.com/drive/folders/10HiQXXMJdisKhBasPi_aKHzJpwqHe1ur
- **Repo GitHub:** https://github.com/Gabo8v/ProyectoNotificacion
- **Plan docx:** https://docs.google.com/document/d/1eW6cN1FZ1_B7Hy2o5GxW77qw3lmdQxIs/edit?usp=drivesdk&ouid=108954821762539778822&rtpof=true&sd=true
- **SESSION.md en Drive:** https://drive.google.com/file/d/1rcMFyf5msNMqKRMUn8hh8ICbQWWzMG7A/view?usp=drivesdk

---

## SESION 25/05/2026 - PR de MaCasamayor + Fixes de estabilidad

### PR fusionado: `feat: autenticacion JWT + cifrado token Gmail + rate limiting + control de polling + seguridad`
- **Autor:** MaCasamayor
- **Branch de revision:** `review/pr-macasamayor` (creada desde `origin/main` post-merge)
- **Commit:** `c3f4570` (merge `fea0a28`)
- **Archivos nuevos:**
  - `app/auth.py` - JWT con python-jose + bcrypt, `require_auth()` middleware helper, `is_authenticated()`
  - `app/limiter.py` - Rate limiting via slowapi (5/min en envio dashboard)
  - `app/routers/auth.py` - Pagina de login (`GET /login`, `POST /login`, `POST /logout`)
  - `app/routers/polling_control.py` - Toggle polling via API (`GET /polling/status`, `POST /polling/toggle`)
- **Archivos modificados:**
  - `app/config.py` - Agregados `ADMIN_USERNAME`, `ADMIN_PASSWORD`, `TOKEN_ENCRYPTION_KEY`, `CORS_ORIGINS`, `WEBHOOK_API_KEY`
  - `app/main.py` - Agregado SessionMiddleware, dashboard_auth_middleware, limiter, polling_control router
  - `app/services/gmail.py` - Cifrado/descifrado de token via Fernet + `TOKEN_ENCRYPTION_KEY`
  - `app/tasks/polling.py` - Respeta `POLLING_ENABLED`
  - `app/routers/dashboard.py` - Rate limiting en POST /dashboard/send
  - `app/templates/base.html` - Boton de toggle polling + link a API Docs
  - `requirements.txt` - Nuevas dependencias: passlib, python-jose[cryptography], slowapi, itsdangerous, bcrypt
- **Credenciales default:** `admin` / `admin123` (desde `app/config.py`)

### Fixes de estabilidad del servidor (aplicados)

| Problema | Causa | Solucion |
|----------|-------|----------|
| Servidor no responde HTTP | `print()` en polling bloqueaba event loop async | Reemplazados `print()` con `logger.warning()` / `logger.error()` en `gmail.py` |
| Servidor se cuelga al iniciar | `creds.refresh(Request())` sin timeout colgaba el startup | Agregado timeout de 10s con `requests_lib.Session` y catch de excepciones |
| `build("gmail", ...)` bloquea el event loop | Llamada HTTP sincronica dentro de async task | Refactorizado `GmailService` a inicializacion diferida (`_ensure()`) y polling movido a `asyncio.to_thread()` |
| Token Gmail expirado (`invalid_grant`) | Token revocado por re-autenticacion | Re-autenticacion manual via OAuth (code guardado con `save_token()`) |
| Spam de `TOKEN_ENCRYPTION_KEY no configurada` | Warning cada 30s en polling | Cambiado a `logger.debug()` |

### Gmail re-autenticado
- Token renovado via OAuth 2.0 (09:19 PM)
- `credentials.json` OK (proyecto: mimetic-card-497013-c2)
- Polling actualmente DESACTIVADO en `main.py` (comentado) para evitar hangs hasta refactorizar a background thread definitivo

### Leccion aprendida / Comportamiento del AI (NO VOLVER A CONGELARSE)
Cuando el AI ejecute acciones como iniciar un servidor o correr un comando largo debe:
1. **No hacer que el usuario tenga que estar pendiente** de si el AI sigue o no — si va a hacer algo pesado, avisa antes
2. **Respuestas cortas y rápidas** — un paso a la vez, sin editar archivos enormes en silencio
3. **Siempre verificar** inmediatamente con un health check (curl, timeout 5s) despues de iniciar un servicio
4. **Timeout explicito** en todos los comandos que puedan colgarse (uso de parametro `timeout` en tool calls)
5. **Auto-diagnostico** si no responde: matar proceso, capturar logs, probar configuracion alternativa
6. **No esperar** a que el usuario reporte "trabado" - detectarlo automaticamente y corregir en el intento
7. Si una estrategia falla 2 veces, cambiar de enfoque en lugar de repetir

### Estado actual al cierre
| Servicio | Puerto | Estado |
|----------|--------|--------|
| FastAPI (uvicorn) | 8000 | ✅ CORRIENDO |
| PostgreSQL (Docker) | 5432 | ✅ CORRIENDO |
| pgAdmin (Docker) | 5050 | ✅ CORRIENDO |
| WhatsApp Bot (Node.js) | 3001 | ✅ CORRIENDO (pm2, desde el proyecto `whatsapp-bot/index.js`) |

---

## SESION 26/05/2026 - Reactivacion de envios (Email + WhatsApp)

### Problema al reanudar
- **Puerto 8000 ocupado** por container `prueba_djangoISDM` -> detenido con `docker stop`
- **WhatsApp bot caido** -> pm2 apuntaba a `C:\Users\Gabo8\OneDrive\Escritorio\whatsapp-sender\bot.js` (version vieja con endpoint `/send` en vez de `/send-message`)
- **Numero de Gabo** en DB: `3875606681` sin codigo de pais -> corregido a `5493875606681`

### Soluciones aplicadas
1. Detenido `prueba_djangoISDM` que ocupaba puerto 8000
2. Eliminado proceso pm2 viejo y creado nuevo apuntando a `whatsapp-bot/index.js` del proyecto
3. Corregido telefono de Gabo en DB: `3875606681` -> `5493875606681`
4. Verificado que pm2 resurrect ejecute el bot correcto (el .bat del escritorio apunta al viejo)

### Estado de envios
| Canal | Prueba | Resultado |
|-------|--------|-----------|
| Email a Gabo | API `/notifications/send` | ✅ sent |
| Email a Mateo | API `/notifications/send` | ✅ sent |
| WhatsApp a Gabo | API `/notifications/send` | ✅ sent (tras corregir numero) |
| WhatsApp a Mateo | API `/notifications/send` | ✅ sent |
| Bot directo | POST `/send-message` | ✅ success |

### Pendiente
- El `.bat` del escritorio (`Iniciar Bot WhatsApp.bat`) usa `pm2 resurrect` que restaura el proceso viejo de `whatsapp-sender`. Habria que actualizarlo o ignorarlo y usar `pm2 start` directamente desde el proyecto.
- Polling Gmail -> WhatsApp sigue desactivado (comentado en `main.py`)

---

## SESION 26/05/2026 (2da parte) - Roles de usuario + Consultas

### Implementacion: Roles (admin/user) + modulo Consultas

#### Cambios en modelos
- **User**: agregados `role` (admin/user) y `password_hash`
- **Nuevo modelo `Consulta`**: id, user_id FK, subject, message, created_at

#### Login unificado por roles
- Misma pagina de login para admin y usuario
- Login verifica contra DB (password_hash con bcrypt)
- `GET /register`, `POST /register`: formulario con nombre, email, whatsapp
- JWT incluye `{"user": ..., "role": ...}`

#### Segregacion por rol en navegacion
| Pagina | Admin | Usuario |
|--------|-------|---------|
| Resumen | ✅ | ✅ (solo sus datos) |
| Enviar | ✅ | ❌ |
| Templates | ✅ | ❌ |
| Historial | ✅ | ❌ |
| Usuarios | ✅ | ❌ |
| Consultas | ✅ | ✅ |
| API Docs | ✅ | ❌ |
| Toggle Polling | ✅ | ❌ |

#### Archivos nuevos/modificados
- `app/models/user.py` - +role, +password_hash
- `app/models/consulta.py` - Nueva tabla
- `app/models/__init__.py` - +Consulta
- `app/auth.py` - require_auth() contra DB, +require_admin(), +get_current_user(), is_authenticated() devuelve role
- `app/routers/auth.py` - Login unificado contra DB, +register GET/POST
- `app/routers/consulta.py` - CRUD de consultas
- `app/routers/dashboard.py` - +user a todos los templates
- `app/templates/base.html` - Nav condicional por role
- `app/templates/consulta.html` - Nueva pagina
- `app/main.py` - +consulta router
- `alembic/versions/f5e556203663_roles_consultas.py` - Migracion

#### Seed data
- **admin** / admin123 (role=admin)
- **usuario** / usuario123 (role=user)
- Admin Desarrollador, Gabo, Mateo tienen password asignado

### Estado al cierre de sesion (26/05/2026)
| Servicio | Puerto | Estado |
|----------|--------|--------|
| FastAPI (uvicorn) | 8000 | ❌ DETENIDO |
| PostgreSQL (Docker) | 5432 | ✅ CORRIENDO |
| pgAdmin (Docker) | 5050 | ✅ CORRIENDO |
| WhatsApp Bot (Node.js) | 3001 | ❌ DETENIDO (pm2 stopped) |

### Para reanudar proxima sesion
```powershell
# Activar entorno
cd C:\Users\Gabo8\OneDrive\Escritorio\ProyectoNotificacion
.venv\Scripts\activate

# Verificar servicios
docker ps | findstr notificaciones     # Deben estar notificaciones-db y notificaciones-pgadmin
pm2 status                              # whatsapp-bot debe estar online

# Si falta PostgreSQL+pgAdmin:
docker-compose up -d

# Si falta WhatsApp bot:
pm2 start whatsapp-bot

# Iniciar FastAPI:
.venv\Scripts\uvicorn app.main:app --reload --port 8000

# Credenciales:
#   Admin:   admin / admin123
#   Usuario: usuario / usuario123

# Iniciar FastAPI (si puerto 8000 ocupado, usar 8001):
.venv\Scripts\uvicorn app.main:app --reload --port 8000
```

---

## SESION 25/05/2026 - Rediseno dashboard dark mode + Login oscuro + Consultas para usuarios

### Resumen
Rediseno completo del frontend del dashboard con tema oscuro tipo ChatGPT:
- Sidebar izquierda fija con navegacion por roles
- Panel central dinamico
- Login con mismo tema dark
- Consultas solo para usuarios no-admin

### Cambios en templates y CSS

#### `app/static/style.css` - Tema oscuro completo
- Fondo `#0d0d0d`, sidebar `#1a1a1a`, superficies `#222`/`#2a2a2a`
- Sidebar fija izquierda con logo, boton "Nueva consulta", buscador, navegacion por secciones
- Stats minimalistas en linea (sin cards con borde)
- Tablas modernas con header oscuro y hover
- Badges de estado (sent/pending/failed) con colores
- Formularios en cards oscuros con bordes sutiles
- Scrollbar personalizado oscuro

#### `app/templates/base.html` - Nuevo layout
- Sidebar izquierda con logo + boton nueva consulta + buscador
- Seccion "Administracion" visible solo para admin (Resumen, Enviar, Templates, Historial, Usuarios)
- Seccion "Consultas" visible solo para usuarios no-admin
- Footer de sidebar con avatar, nombre, rol y boton de cerrar sesion
- Flash messages entre sidebar y contenido

#### `app/templates/index.html` - Resumen segregado
- Admin: stats de notificaciones (total, enviadas, pendientes, fallidas, usuarios, templates) + tabla ultimas 10
- User: stats de consultas (total, respondidas) + link a modulo consultas

#### `app/templates/send.html` - Formulario + panel consultas
- Panel derecho reemplazado: ahora muestra **consultas pendientes** (sin responder) en vez de notificaciones pendientes
- Consultas clickeables: al hacer clic, cargan asunto, mensaje y usuario en el formulario de envio
- Selector de canal, usuario, template (eliminado por claridad)

#### `app/templates/consulta.html` - Nueva pagina de consultas
- Formulario para crear consulta (asunto + mensaje)
- Historial de consultas del usuario con respuestas

#### `app/templates/history.html`, `users.html` - Actualizados
- Adaptados al nuevo layout de sidebar + main-header + main-content

#### `app/routers/auth.py` - Login dark
- CSS inline actualizado al mismo tema oscuro (`#0d0d0d`, `#1a1a1a`, `#2a2a2a`)
- Cache prevenido con meta tag

#### `app/routers/consulta.py` - Proteccion admin
- Admin redirigido a `/dashboard/` si intenta acceder a consultas

#### `app/routers/dashboard.py` - Consultas en formulario de envio
- Ruta `/dashboard/send` ahora pasa `pending_consultas` (consultas sin `response`) en vez de notificaciones pendientes

#### `app/models/consulta.py` - Relacion User
- Agregada relacion `user: Mapped["User"] = relationship("User", lazy="joined")` para acceso a `c.user.name`

### Problema tecnico: Puerto 8000 zombie
- Puerta 8000 quedo ocupada por procesos Python zombie (no detectables por `taskkill`)
- Solucion: usar puerto 8001 como alternativa
- Causa: multiples instancias de uvicorn con `--reload` dejaban procesos hijos huerfanos en Windows

### Estado al cierre de sesion (25/05/2026)
| Servicio | Puerto | Estado |
|----------|--------|--------|
| FastAPI (uvicorn) | 8001 | ✅ CORRIENDO |
| PostgreSQL (Docker) | 5432 | ✅ CORRIENDO |
| pgAdmin (Docker) | 5050 | ✅ CORRIENDO |
| WhatsApp Bot (Node.js) | 3001 | ✅ CORRIENDO (proceso directo) |

### Pendiente
- Puerto 8000 sigue ocupado por zombie TCP hasta reinicio de Windows
- Polling Gmail -> WhatsApp sigue desactivado (comentado en `main.py`)

---

## SESION 26/05/2026 (3ra parte) - Auto-start WhatsApp bot + Open Design

### Open Design descargado
- Repo clonado: `C:\Users\Gabo8\OneDrive\Escritorio\open-design`
- Dependencias instaladas con `pnpm install` (Node 24 + pnpm 10.33.2 via corepack)
- Se ejecuto en puertos efimeros: daemon `:63586`, web `:63587`
- Pendiente para futura integracion como generador de UI

### Fix: WhatsApp bot caido
- **Problema:** `pm2 list` mostraba `whatsapp-bot` como `stopped`, puerto 3001 no escuchaba
- **Solucion inmediata:** `pm2 start whatsapp-bot` (ahora pm2 apunta correctamente a `whatsapp-bot/index.js`)

### Feature: Auto-verificacion del bot al iniciar el proyecto
Se agregaron dos mecanismos para que el bot arranque automaticamente:

#### `app/main.py` - `_verificar_bot()` en lifespan
- Se ejecuta como `asyncio.create_task()` al arrancar FastAPI (antes del yield del lifespan)
- **Paso 1:** GET a `http://localhost:3001/health` (timeout 5s) — si responde 200, ok
- **Paso 2:** Si no responde, ejecuta `pm2.cmd start whatsapp-bot` via `subprocess.run()` + `asyncio.to_thread()`
- **Paso 3:** Si pm2 falla, ejecuta `node index.js` directamente desde `whatsapp-bot/`
- Usa `shutil.which()` para resolver rutas absolutas de `node` y `pm2.cmd`
- Usa `capture_output=True` con decode `utf-8 errors='replace'` para evitar crash por Unicode

#### `iniciar.bat` - Refactorizado
- Nueva subrutina `:iniciar_bot` que prioriza pm2:
  1. Si `pm2` existe en PATH, chequea si `whatsapp-bot` ya esta online
  2. Si no, ejecuta `pm2 start whatsapp-bot`
  3. Si pm2 falla o no existe, cae al metodo anterior (ventana `cmd /c node index.js`)
- El script principal llama `call :iniciar_bot` y aborta si falla

#### Prueba realizada
1. WhatsApp bot detenido (`pm2 stop`) -> puerto 3001 cerrado
2. FastAPI iniciado en puerto 8002 con el nuevo codigo
3. Lifespan ejecuto `_verificar_bot()` -> detecto bot caido -> lo inicio via pm2
4. Verificado: bot online (PID 2432), puerto 3001 escuchando, health endpoint ok

### Nota tecnica para Windows
- `asyncio.create_subprocess_exec` no es confiable bajo uvicorn+Windows para comandos tipo `.cmd`
- Solucion: usar `asyncio.to_thread()` + `subprocess.run()` del modulo sincronico
- `shutil.which()` resuelve rutas absolutas necesarias para subprocess

### Estado al cierre de sesion (26/05/2026 - 3ra parte)
| Servicio | Puerto | Estado |
|----------|--------|--------|
| FastAPI (uvicorn) | 8002 | ❌ DETENIDO |
| PostgreSQL (Docker) | 5432 | ✅ CORRIENDO |
| pgAdmin (Docker) | 5050 | ✅ CORRIENDO |
| WhatsApp Bot (Node.js) | 3001 | ❌ DETENIDO (pm2 stopped) |
| Open Design | 63586/63587 | ❌ DETENIDO |

### Para reanudar
```powershell
cd C:\Users\Gabo8\OneDrive\Escritorio\ProyectoNotificacion
.venv\Scripts\activate
docker ps | findstr notificaciones     # Verificar PostgreSQL+pgAdmin
docker-compose up -d                   # Si faltan
.venv\Scripts\uvicorn app.main:app --reload --port 8000  # FastAPI (auto-arranca bot)
# Si puerto 8000 zombie, usar --port 8001 o 8002
```

### Archivos modificados
- `app/main.py` - Import asyncio, subprocess, shutil, httpx; agregada `_verificar_bot()`
- `iniciar.bat` - Refactorizado con subrutina `:iniciar_bot` (pm2 priority)

---

## SESION 26/05/2026 (4ta parte) - Frontend Linear Design + Fix bot + QR PNG

### Resumen
Modernización del frontend del dashboard con tema oscuro usando OKLCH tokens de Open Design (Linear). Fix permanente de pm2 con rutas explícitas. QR regenerado como PNG para escaneo fiable.

### Cambios en CSS y login

#### `app/static/style.css` - Tokens Linear Design System
- **Fondo:** `#08090a`, tarjetas `#0f1011`, superficie `rgba(255,255,255,0.03)`
- **Texto:** `#f7f8f8` primario, `#8a8f98` secundario, `#62666d` terciario
- **Acento:** `#5e6ad2` / hover `#828fff` (OKLCH)
- **Bordes:** `rgba(255,255,255,0.08)` y `rgba(255,255,255,0.05)`
- **Tipografía:** Inter Variable con `cv01`, `ss03`
- **Badges:** pill-style con radio 9999px
- **Botones:** ghost con borde fino (sin bg sólido)
- **Inputs:** dark con foco `box-shadow`

#### `app/routers/auth.py` - Login/register con tabs
- Página única con tabs "Iniciar sesión" / "Registrarse"
- OKLCH tokens inline (bg, surface, card, fg, muted, border, accent)
- Inter font, uppercase labels, inputs con borde y focus shadow
- Alertas error/success inline
- Form login: username + password; register: username + password + email + WhatsApp
- Fix: `KeyError: 'box-sizing'` resuelto cambiando `.format()` por `.replace()`

### Fixes de infraestructura

| Problema | Solución |
|----------|----------|
| pm2 apuntaba a `whatsapp-sender/bot.js` viejo | `pm2 delete whatsapp-bot` + `pm2 start whatsapp-bot/index.js --name whatsapp-bot` con ruta absoluta |
| `_verificar_bot()` usaba nombre de proceso no fiable | Cambiado a ruta absoluta `C:\Users\Gabo8\...\whatsapp-bot\index.js` |
| `iniciar.bat` usaba nombre relativo | Cambiado a `%~dp0whatsapp-bot\index.js` explícito |
| Webhook del bot apuntaba a `:8000` | Actualizado a `:8002` |
| Puerto 8000/8001 zombie | Servidor movido a puerto 8002 |
| Sesión WhatsApp perdida al migrar de `whatsapp-sender` | Eliminado `.wwebjs_auth` corrupto, generado QR nuevo como PNG |

### QR como imagen PNG
- Instalado paquete `qrcode` (npm) en `whatsapp-bot/`
- Modificado `index.js`: en evento `qr`, genera `qr.png` (512x512) en raíz del proyecto
- Nuevo endpoint `GET /qr-image`: sirve QR como HTML con imagen PNG embebida
- Nuevo endpoint `GET /qr-raw`: devuelve QR como data URL JSON
- QR escaneado exitosamente -> sesión autenticada y persistente

### Estado al cierre de sesion (26/05/2026 - 4ta parte)
| Servicio | Puerto | Estado |
|----------|--------|--------|
| FastAPI (uvicorn) | 8002 | ❌ DETENIDO |
| PostgreSQL (Docker) | 5432 | ✅ CORRIENDO |
| pgAdmin (Docker) | 5050 | ✅ CORRIENDO |
| WhatsApp Bot (Node.js) | 3001 | ✅ CORRIENDO (pm2, sesión autenticada) |

### Para reanudar
```powershell
cd C:\Users\Gabo8\OneDrive\Escritorio\ProyectoNotificacion
.venv\Scripts\activate
docker-compose up -d                                 # PostgreSQL + pgAdmin
pm2 start whatsapp-bot                               # WhatsApp (se auto-conecta)
.venv\Scripts\uvicorn app.main:app --reload --port 8002
# Credenciales: admin/admin123 (admin), usuario/usuario123 (user)
```

### Archivos modificados
- `app/static/style.css` - Tokens Linear Design System (OKLCH)
- `app/routers/auth.py` - Login/register con tabs + OKLCH tokens
- `whatsapp-bot/index.js` - +qr-code package, +qr.png, +/qr-image, +/qr-raw
- `whatsapp-bot/package.json` - +dependencia qrcode
- `app/services/whatsapp.py` - send_message() con @c.us auto (existente)
- `app/main.py` - _verificar_bot() con ruta absoluta
- `iniciar.bat` - puerto 8002, ruta explícita al bot
```
