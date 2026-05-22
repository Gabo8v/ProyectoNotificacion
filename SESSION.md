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
| FastAPI (uvicorn) | 8000 | ❌ DETENIDO (habia que matarlo) |
| PostgreSQL (Docker) | 5432 | ✅ CORRIENDO (docker) |
| pgAdmin (Docker) | 5050 | ✅ CORRIENDO (docker) |
| WhatsApp Bot (Node.js) | 3001 | ❌ DETENIDO (habia que matarlo) |

### Para reanudar la sesion, ejecutar en orden:
```powershell
# 1. Activar entorno
cd C:\Users\Gabo8\OneDrive\Escritorio\ProyectoNotificacion
.venv\Scripts\activate

# 2. Verificar PostgreSQL
docker ps | findstr notificaciones

# 3. Iniciar WhatsApp bot (nueva terminal)
cd whatsapp-bot && npm run dev

# 4. Iniciar FastAPI
.venv\Scripts\uvicorn app.main:app --reload --port 8000
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

## FASE 5 - Integracion Bidireccional ⏳ (PENDIENTE - PROXIMA)

### Que hay que implementar

#### 5a. Gmail -> WhatsApp (polling)
- Crear un background task/timer en FastAPI que cada N segundos llame a `GmailService.read_inbox()`
- Por cada correo no leido, crear una Notification y enviarla por WhatsApp via `WhatsAppService.send_message()`
- Marcar el correo como leido via `GmailService.mark_as_read()`
- Guardar la relacion entre message_id de Gmail y el numero de WhatsApp en `conversation_ref`

#### 5b. WhatsApp -> Gmail (respuesta automatica)
- En el webhook `/whatsapp/webhook`, detectar keywords en el mensaje
- Buscar en `Template` si alguna keyword coincide
- Si coincide, obtener el destinatario original y usar `GmailService.send_email()` para responder
- Guardar la notification en DB

#### 5c. Matching de hilos
- Cuando llega un correo de X persona, guardar su email como `conversation_ref` en la Notification
- Cuando responde por WhatsApp, usar ese `conversation_ref` para saber a quien responder por Gmail
- Formato sugerido: `gmail:<message_id>` o `wa:<phone>@c.us`

### Archivos a modificar para Fase 5
- `app/services/notification_service.py` - Agregar logica de matching
- `app/routers/whatsapp.py` - Procesar templates y responder
- **CREAR** `app/services/integration_service.py` - Orquestar el flujo bidireccional
- **CREAR** `app/tasks/polling.py` - Background task para polling de Gmail

### Dependencias nuevas que pueden hacer falta
- `apscheduler` o `fastapi-utils` para background tasks
- Ya estaria cubierto con `asyncio` + `BackgroundTasks` de FastAPI

---

## FASE 6 - Dashboard ⏳ (PENDIENTE)

- Panel web con HTML + CSS + JS o Jinja2
- Pagina de inicio con resumen (ultimas notificaciones)
- Formulario para enviar notificaciones manualmente
- CRUD de templates desde la UI
- Historial con busqueda por fecha y texto
- Usar Jinja2 (ya incluido como dependencia de FastAPI) o armar API + frontend separado

---

## FASE 7 - Documentacion y Tests ⏳ (PENDIENTE)

- Tests con pytest + httpx (test client de FastAPI)
- README completo con capturas
- Guia de instalacion para nuevo desarrollador
- Postman/Thunder Client collection para los endpoints

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
