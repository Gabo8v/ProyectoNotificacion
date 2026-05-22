# SESSION LOG - Sistema de Gestion de Notificaciones

## Informacion General

- **Proyecto:** Sistema de Gestion de Notificaciones
- **Stack:** Python (FastAPI) + PostgreSQL + whatsapp-web.js (Node.js)
- **Repo:** https://github.com/Gabo8v/ProyectoNotificacion
- **Colaboradores:** Gabo8v, luismateocasamayor (Mateo)
- **Drive Compartido:** https://drive.google.com/drive/folders/10HiQXXMJdisKhBasPi_aKHzJpwqHe1ur

---

## FASE 1 - Setup del Proyecto ✅ (COMPLETADA)

### Archivos creados
| Archivo | Proposito |
|---------|-----------|
| `app/main.py` | Entry point FastAPI |
| `app/config.py` | Variables de entorno (pydantic-settings) |
| `app/database.py` | SQLAlchemy + conexion |
| `app/models/user.py` | Modelo User |
| `app/models/notification.py` | Modelo Notification (channel, status, conversation_ref) |
| `app/models/template.py` | Modelo Template (keywords, body) |
| `app/models/log.py` | Modelo Log (channel, level) |
| `app/routers/health.py` | GET /health |
| `app/routers/notifications.py` | POST /send, GET /history (esqueletos) |
| `app/routers/templates.py` | GET /, POST / (esqueletos) |
| `app/schemas/notification.py` | Pydantic: NotificationOut, NotificationCreate |
| `app/schemas/template.py` | Pydantic: TemplateOut, TemplateCreate |
| `app/services/gmail.py` | **Completado** - GmailService |
| `app/services/whatsapp.py` | Placeholder |
| `app/services/notification_service.py` | Placeholder |
| `whatsapp-bot/package.json` | Dependencias Node.js |
| `whatsapp-bot/index.js` | Bot con Express + whatsapp-web.js |
| `docker-compose.yml` | PostgreSQL 15 + pgAdmin |

### Decisiones tomadas
- Base de datos: PostgreSQL (no SQLite)
- Modelos con UUID como PK
- Enums para channel (email/whatsapp) y status (pending/sent/failed)
- Conversation_ref para tracking de hilos bidireccional

---

## FASE 2 - Gmail API ✅ (COMPLETADA)

### Estado
- Gmail API habilitada en proyecto: `mimetic-card-497013-c2`
- Credenciales OAuth 2.0 (Desktop App)
- Autenticacion completada con scope `gmail.modify`

### Archivos sensibles (NO subir a Git)
- `credentials.json` - client_id + client_secret
- `gmail_token.pickle` - token OAuth de Gmail

### Funcionalidades implementadas
- `GmailService.send_email(to, subject, body)` -> dict | None
- `GmailService.read_inbox(max_results=5)` -> list[dict]
- `GmailService.mark_as_read(message_id)` -> bool
- Auth flow: `get_service()` con refresh automatico

### Progreso real
- ✅ Lectura de bandeja: 3 correos no leidos
- ✅ Envio a luismateocasamayor@gmail.com: exitoso

---

## FASE 3 - Bot WhatsApp ⏳ (PENDIENTE)

### Lo que hay que hacer
1. Tener Node.js instalado
2. `cd whatsapp-bot && npm install`
3. Verificar que puppeteer/chromium funciona
4. Escanear QR con el telefono
5. Probar envio desde FastAPI al bot (HTTP local)
6. Probar recepcion: WhatsApp -> Node -> FastAPI

### Estado actual
- `whatsapp-bot/package.json` creado con dependencias
- `whatsapp-bot/index.js` creado con:
  - Cliente whatsapp-web.js
  - Servidor Express en puerto 3001
  - Endpoint POST /send-message
  - Endpoint GET /health
  - Webhook que reenvia mensajes a FastAPI en /whatsapp/webhook

---

## FASE 4 - Core Notificaciones ⏳ (PENDIENTE)

- Implementar NotificationService.send()
- Implementar NotificationService.get_history()
- Conectar routers con servicios reales (DB)
- Logging de todas las operaciones

---

## FASE 5 - Integracion Bidireccional ⏳ (PENDIENTE)

- Gmail -> WhatsApp: polling de bandeja -> notificar por bot
- WhatsApp -> Gmail: mensaje entrante -> enviar correo
- Sistema de matching de hilos (conversation_ref)

---

## FASE 6 - Dashboard ⏳ (PENDIENTE)

- Panel web simple
- Envio manual, historial, templates CRUD

---

## FASE 7 - Documentacion ⏳ (PENDIENTE)

- README completo
- Tests

---

## Comandos utiles

```bash
# Iniciar servidor FastAPI
.venv\Scripts\uvicorn app.main:app --reload --port 8000

# Iniciar PostgreSQL
docker-compose up -d

# Iniciar WhatsApp bot
cd whatsapp-bot && npm run dev

# Activar entorno virtual
.venv\Scripts\activate

# Instalar dependencias
.venv\Scripts\pip install -r requirements.txt
```

## Links rapidos

- **Drive compartido:** https://drive.google.com/drive/folders/10HiQXXMJdisKhBasPi_aKHzJpwqHe1ur
- **Repo GitHub:** https://github.com/Gabo8v/ProyectoNotificacion
- **Plan docx:** https://docs.google.com/document/d/1eW6cN1FZ1_B7Hy2o5GxW77qw3lmdQxIs/edit?usp=drivesdk&ouid=108954821762539778822&rtpof=true&sd=true
