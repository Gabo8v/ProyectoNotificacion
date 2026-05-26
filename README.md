# Sistema de Gestion de Notificaciones

Plataforma de notificaciones multicanal con integracion Gmail + WhatsApp, respuestas automaticas via templates y dashboard web.

## Stack

| Componente | Tecnologia |
|------------|-----------|
| Backend | Python 3.12 / FastAPI |
| Base de datos | PostgreSQL 15 (Docker) |
| ORM | SQLAlchemy 2.0 + Alembic |
| Gmail | google-api-python-client (OAuth 2.0) |
| WhatsApp | whatsapp-web.js (Node.js) |
| Dashboard | Jinja2 + CSS dark mode |
| Infra | Docker Compose |
| Tests | pytest + httpx |

## Estructura

```
ProyectoNotificacion/
├── app/
│   ├── main.py                 # Entry point FastAPI
│   ├── config.py               # Settings via pydantic-settings
│   ├── database.py             # SQLAlchemy engine + session
│   ├── auth.py                 # JWT + bcrypt + role verification
│   ├── limiter.py              # Rate limiting (slowapi)
│   ├── models/                 # SQLAlchemy models
│   │   ├── user.py             # User (id, name, email, phone, role, password_hash)
│   │   ├── notification.py     # Notification (channel, status, refs)
│   │   ├── template.py         # Template (keywords, subject, body)
│   │   ├── consulta.py         # Consulta (user inquiries, response workflow)
│   │   └── log.py              # Audit log
│   ├── routers/                # REST + Web endpoints
│   │   ├── auth.py             # GET/POST /login, /register, /logout
│   │   ├── health.py           # GET /health
│   │   ├── notifications.py    # POST /notifications/send, GET /history
│   │   ├── templates.py        # CRUD /templates/
│   │   ├── whatsapp.py         # POST /whatsapp/webhook
│   │   ├── consulta.py         # GET/POST /dashboard/consulta
│   │   ├── dashboard.py        # Jinja2 dashboard web
│   │   └── polling_control.py  # GET/POST /polling/toggle
│   ├── schemas/                # Pydantic request/response
│   ├── services/
│   │   ├── gmail.py            # GmailService (send, read, mark_read)
│   │   ├── whatsapp.py         # WhatsAppService (send_message)
│   │   ├── notification_service.py  # Logica de negocio
│   │   └── integration_service.py   # Flujo bidireccional
│   ├── tasks/
│   │   └── polling.py          # Polling Gmail -> WhatsApp cada 30s
│   ├── templates/              # Jinja2 HTML templates (dark theme)
│   │   ├── base.html           # Sidebar layout izquierda
│   │   ├── index.html          # Resumen con metricas
│   │   ├── send.html           # Formulario + consultas pendientes
│   │   ├── templates.html      # CRUD de templates
│   │   ├── history.html        # Historial con filtros
│   │   ├── users.html          # Gestion de usuarios
│   │   └── consulta.html       # Consultas de usuario
│   └── static/
│       └── style.css           # CSS dark mode + sidebar responsive
├── whatsapp-bot/               # Bot Node.js (whatsapp-web.js)
├── tests/                      # pytest suite
├── docker-compose.yml          # PostgreSQL + pgAdmin
└── .env.example
```

## Setup rapido

### Prerrequisitos

- Python 3.12
- Node.js 24+
- Docker Desktop
- Brave/Chrome (para sesion de WhatsApp)

### 1. Clonar e instalar

```bash
git clone https://github.com/Gabo8v/ProyectoNotificacion.git
cd ProyectoNotificacion
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### 2. Base de datos

```bash
docker-compose up -d
```

### 3. Variables de entorno

```bash
cp .env.example .env
# Editar .env con tus valores
```

### 4. WhatsApp bot

```bash
cd whatsapp-bot
npm install
npm run dev
# Escanear QR con WhatsApp en la primera ejecucion
```

### 5. Gmail API

```bash
# Colocar credentials.json en la raiz (descargar de Google Cloud Console)
python -c "from app.services.gmail import auth_url; auth_url()"
# Visitar URL, autorizar, pegar el codigo:
python -c "from app.services.gmail import save_token; save_token('CODIGO')"
```

### 6. Iniciar servidor

```bash
.venv\Scripts\uvicorn app.main:app --reload --port 8000
```

### 7. Tests

```bash
.venv\Scripts\pytest tests/ -v
```

## Endpoints REST

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/notifications/send` | Enviar notificacion |
| GET | `/notifications/history` | Historial con filtros |
| GET | `/templates/` | Listar templates |
| POST | `/templates/` | Crear template |
| DELETE | `/templates/{id}` | Eliminar template |
| POST | `/whatsapp/webhook` | Webhook de WhatsApp |

## Dashboard Web

`http://localhost:8000/dashboard/`

- Tema oscuro tipo ChatGPT con sidebar izquierda fija
- Resumen con metricas separadas por rol (admin ve todas, usuario solo consultas)
- Envio manual de notificaciones con panel de consultas pendientes clickeables
- CRUD de templates
- Gestion de usuarios
- Historial con filtros y paginacion
- Modulo de consultas para usuarios no-admin

### Credenciales

| Rol | Usuario | Password |
|-----|---------|----------|
| Admin | `admin` | `admin123` |
| Usuario | `usuario` | `usuario123` |

## Flujo de integracion

```
Gmail (correo nuevo)
  → polling cada 30s
  → IntegrationService.email_to_whatsapp()
  → WhatsApp del usuario

WhatsApp (respuesta del usuario)
  → POST /whatsapp/webhook
  → IntegrationService.whatsapp_to_email()
  → Busca template por keyword
  → Envia email automaticamente
```

## Archivos sensibles (NO commitar)

- `credentials.json` - Gmail OAuth client
- `gmail_token.pickle` - Gmail OAuth token
- `.env` - Configuracion
- `whatsapp-bot/.wwebjs_auth/` - Sesion de WhatsApp
