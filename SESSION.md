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

## FASE 3 - Bot WhatsApp ✅ (COMPLETADA)

### Estado
- Node.js 24.16.0 + npm 11.13.0
- Dependencias instaladas (puppeteer usa Brave existente)
- QR escaneado y sesion guardada (LocalAuth)
- Bot autenticado y funcionando

### Archivos
| Archivo | Proposito |
|---------|-----------|
| `whatsapp-bot/index.js` | Cliente whatsapp-web.js + Express en puerto 3001 |
| `whatsapp-bot/package.json` | Dependencias: whatsapp-web.js, qrcode-terminal, express |
| `app/services/whatsapp.py` | WhatsAppService con send_message() y formato automatico @c.us |
| `app/routers/whatsapp.py` | POST /whatsapp/webhook para recibir mensajes del bot |

### Configuracion especial
- Puppeteer usa Brave: `executablePath: "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"`
- Formato de numero WhatsApp: `5493875360385@c.us` (codigo pais + 9 + numero + @c.us)
- Sesion guardada en carpeta `.wwebjs_auth/` (no subir a git)

### Progreso real
- ✅ QR escaneado y sesion conectada
- ✅ Envio de mensaje a 3875360385: "Hola amigo mio" -> exito
- ✅ HTTP endpoint /send-message funcional
- ✅ Webhook /whatsapp/webhook recibe mensajes entrantes
- ✅ FastAPI corriendo en puerto 8000 con whatsapp router incluido

---

## FASE 4 - Core Notificaciones ✅ (COMPLETADA)

### Estado
- PostgreSQL corriendo en Docker (puerto 5432)
- pgAdmin en puerto 5050 (admin@notificaciones.com / admin)
- Migraciones Alembic ejecutadas (tablas: users, notifications, templates, logs)
- NotificationService implementado con DB real

### Endpoints funcionales
| Metodo | Ruta | Proposito |
|--------|------|-----------|
| POST | `/notifications/send` | Crear notificacion |
| GET | `/notifications/history` | Historial con filtros (channel, status, limit, offset) |
| GET | `/templates/` | Listar plantillas |
| POST | `/templates/` | Crear plantilla |
| DELETE | `/templates/{id}` | Eliminar plantilla |

### Progreso real
- ✅ PostgreSQL + pgAdmin levantados con docker-compose
- ✅ Alembic autogenerate + upgrade (4 tablas creadas)
- ✅ POST /notifications/send -> 200 (crea registro en DB)
- ✅ GET /notifications/history -> 200 (devuelve listado)
- ✅ POST /templates/ -> 200 (crea plantilla)
- ✅ GET /templates/ -> 200 (lista plantillas)
- ✅ NotificationService con send(), mark_sent(), mark_failed(), get_history(), log()

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
