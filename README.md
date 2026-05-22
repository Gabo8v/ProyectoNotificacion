# Sistema de Gestion de Notificaciones

Modulo de notificaciones con integracion Gmail + WhatsApp Bot + respuestas predefinidas.

## Stack

- **Backend:** Python 3.11+ / FastAPI
- **Base de datos:** PostgreSQL 15 (Docker)
- **ORM:** SQLAlchemy 2.0 + Alembic
- **Gmail:** google-api-python-client
- **WhatsApp:** whatsapp-web.js (Node.js)
- **Infra:** Docker Compose

## Estructura

```
ProyectoNotificacion/
├── app/                  # Codigo Python (FastAPI)
│   ├── main.py           # Punto de entrada
│   ├── config.py         # Configuracion (variables de entorno)
│   ├── database.py       # Conexion a base de datos
│   ├── models/           # Modelos SQLAlchemy
│   ├── routers/          # Endpoints REST
│   ├── schemas/          # Pydantic schemas
│   └── services/         # Logica de negocio
├── whatsapp-bot/         # Bot de WhatsApp (Node.js)
├── docker-compose.yml    # PostgreSQL + pgAdmin
├── requirements.txt
└── .env.example
```

## Setup para desarrollo

### 1. Clonar e instalar dependencias Python

```bash
python -m venv .venv
source .venv/bin/activate   # o .venv\Scripts\activate en Windows
pip install -r requirements.txt
```

### 2. Base de datos

```bash
docker-compose up -d
```

### 3. Configurar variables de entorno

```bash
cp .env.example .env
```

### 4. WhatsApp bot

```bash
cd whatsapp-bot
npm install
npm run dev
```

### 5. Iniciar servidor

```bash
uvicorn app.main:app --reload --port 8000
```

## Flujo de trabajo Git

1. Cada desarrollador trabaja en su rama
2. Hacer `git pull` antes de empezar
3. Commits frecuentes con mensajes descriptivos en espanol
4. Al terminar una fase, hacer merge a main
