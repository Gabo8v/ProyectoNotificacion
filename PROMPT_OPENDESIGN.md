# Prompt: Aplicar Linear Design System a templates del Dashboard

Aplicar los mismos tokens de **Linear Design System (Open Design)** que ya se aplicaron a `app/static/style.css` y `app/routers/auth.py` a los siguientes 6 templates Jinja2 de `app/templates/`.

El CSS ya está completo y funcional en `style.css`. Cada template hereda del layout `base.html`.

---

## Design Tokens (ya en style.css)

```css
--bg: #08090a;
--sidebar: #0f1011;
--surface: rgba(255,255,255,0.03);
--surface2: #191a1b;
--hover: rgba(255,255,255,0.06);
--border: rgba(255,255,255,0.08);
--border-subtle: rgba(255,255,255,0.05);
--text: #f7f8f8;
--text2: #8a8f98;
--text3: #62666d;
--accent: #5e6ad2;
--accent-hover: #828fff;
--green: #10b981;
--red: #ef4444;
--yellow: #eab308;
--radius: 6px;
--sidebar-w: 260px;
```

## Tipografía

- `font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`
- `font-feature-settings: 'cv01', 'ss03'`
- Font weights: título/tab-header `510`, normal `400`, secondary `.7rem`

## Clases CSS disponibles (usar estas, NO estilos inline)

**Sidebar:** `.sidebar`, `.sidebar-header`, `.sidebar-logo`, `.btn-new`, `.sidebar-search`, `.sidebar-nav`, `.sidebar-section`, `.sidebar-section-title`, `.sidebar-item`, `.sidebar-item.active`, `.sidebar-item .icon`, `.sidebar-footer`, `.sidebar-user`, `.sidebar-avatar`, `.sidebar-user-info`, `.sidebar-user-name`, `.sidebar-user-role`

**Layout:** `.main`, `.main-header`, `.main-title`, `.main-content`

**Stats:** `.stats`, `.stat`, `.stat-label`, `.stat-value`

**Cards/Form:** `.card`, `.form-card`, `.form-group`, `label`, `input`, `select`, `textarea`, `button`, `.btn`, `.btn-primary`, `.btn-secondary`, `.btn-danger`

**Tabla:** `.table-container`, `<table>`, `<th>`, `<td>`

**Badges:** `.badge`, `.badge-sent`, `.badge-pending`, `.badge-failed`, `.badge-email`, `.badge-whatsapp`

**Feedback:** `.flash`, `.flash-success`, `.flash-error`, `.empty-state`

**Pagination:** `.pagination`, `.pagination a`, `.pagination .current`

**Consultas:** `.consulta-item`, `.consulta-item .subject`, `.consulta-item .meta`, `.consulta-item .response-box`

**Filtros:** `.filters`

---

## Reglas

1. **No modificar** `style.css` ni `auth.py`
2. **No cambiar** la lógica Jinja2 (variables, loops, blocks, extends, conditions)
3. **Reemplazar** todo `style="..."` inline por las clases CSS correspondientes
4. **Mantener** grids de 2 columnas (`style="display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;align-items:start;"`)
5. **No mover** bloques ni cambiar estructura HTML
6. Los items de templates y usuarios (que son como cards) deberían usar clase `.card` o similar en vez de inline `background:var(--surface);border:...`
7. Para colores en stat-values usar solo `style="color:var(--green)"` inline (única excepción)

---

## Templates a transformar

### 1. base.html (layout — NO TOCAR, ya está correcto)
```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Dashboard{% endblock %} — Notificaciones</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
<aside class="sidebar">
    <div class="sidebar-header">
        <div class="sidebar-logo">◆ <span>Notificaciones</span></div>
        <a href="/dashboard/consulta" class="btn-new">
            <span>+</span> <span>Nueva consulta</span>
        </a>
        <input class="sidebar-search" type="text" placeholder="Buscar...">
    </div>
    <nav class="sidebar-nav">
        {% if user and user.role == 'admin' %}
        <div class="sidebar-section">
            <div class="sidebar-section-title">Administración</div>
            <a href="/dashboard/" class="sidebar-item {% if request.url.path == '/dashboard/' %}active{% endif %}">
                <span class="icon">◇</span> <span>Resumen</span>
            </a>
            <a href="/dashboard/send" class="sidebar-item {% if request.url.path == '/dashboard/send' %}active{% endif %}">
                <span class="icon">▶</span> <span>Enviar</span>
            </a>
            <a href="/dashboard/templates" class="sidebar-item {% if request.url.path == '/dashboard/templates' %}active{% endif %}">
                <span class="icon">☰</span> <span>Templates</span>
            </a>
            <a href="/dashboard/history" class="sidebar-item {% if request.url.path == '/dashboard/history' %}active{% endif %}">
                <span class="icon">◎</span> <span>Historial</span>
            </a>
            <a href="/dashboard/users" class="sidebar-item {% if request.url.path == '/dashboard/users' %}active{% endif %}">
                <span class="icon">●</span> <span>Usuarios</span>
            </a>
        </div>
        {% endif %}
        {% if not user or user.role != 'admin' %}
        <div class="sidebar-section">
            <div class="sidebar-section-title">Consultas</div>
            <a href="/dashboard/consulta" class="sidebar-item {% if request.url.path == '/dashboard/consulta' %}active{% endif %}">
                <span class="icon">○</span> <span>Mis consultas</span>
            </a>
        </div>
        {% endif %}
    </nav>
    <div class="sidebar-footer">
        <div class="sidebar-user">
            <div class="sidebar-avatar">{{ user.name[0]|upper if user else '?' }}</div>
            <div class="sidebar-user-info">
                <div class="sidebar-user-name">{{ user.name if user else 'Invitado' }}</div>
                <div class="sidebar-user-role">{{ user.role if user else '—' }}</div>
            </div>
            <form method="post" action="/logout" style="margin:0;">
                <button type="submit" style="background:none;border:none;color:var(--text2);cursor:pointer;font-size:0.8rem;padding:0.25rem;" title="Cerrar sesion">↩</button>
            </form>
        </div>
    </div>
</aside>
<main class="main">
    {% if flash %}
    <div style="padding: 1rem 2rem 0;">
        <div class="flash flash-{{ flash.type }}">{{ flash.message }}</div>
    </div>
    {% endif %}
    {% block content %}{% endblock %}
</main>
</body>
</html>
```

---

### 2. index.html (resumen)
```html
{% extends "base.html" %}
{% block title %}Resumen{% endblock %}
{% block content %}
<div class="main-header">
    <h1 class="main-title">Resumen</h1>
</div>
<div class="main-content">
{% if user and user.role == 'admin' %}
<div class="stats">
    <div class="stat"><span class="stat-label">Notificaciones</span><span class="stat-value">{{ total }}</span></div>
    <div class="stat"><span class="stat-label">Enviadas</span><span class="stat-value" style="color:var(--green)">{{ sent }}</span></div>
    <div class="stat"><span class="stat-label">Pendientes</span><span class="stat-value" style="color:var(--yellow)">{{ pending }}</span></div>
    <div class="stat"><span class="stat-label">Fallidas</span><span class="stat-value" style="color:var(--red)">{{ failed }}</span></div>
    <div class="stat"><span class="stat-label">Usuarios</span><span class="stat-value">{{ total_users }}</span></div>
    <div class="stat"><span class="stat-label">Templates</span><span class="stat-value">{{ total_templates }}</span></div>
</div>
<h2 style="font-size:1rem;font-weight:500;margin-bottom:0.75rem;">Ultimas notificaciones</h2>
{% if latest %}
<div class="table-container">
<table>
    <thead>
        <tr>
            <th>Fecha</th>
            <th>Canal</th>
            <th>Usuario</th>
            <th>Asunto</th>
            <th>Estado</th>
        </tr>
    </thead>
    <tbody>
        {% for n in latest %}
        <tr>
            <td>{{ n.created_at.strftime('%d/%m %H:%M') }}</td>
            <td><span class="badge badge-{{ n.channel.value }}">{{ n.channel.value }}</span></td>
            <td>{{ n.user.name if n.user else '—' }}</td>
            <td>{{ n.subject or '(sin asunto)' }}</td>
            <td><span class="badge badge-{{ n.status.value }}">{{ n.status.value }}</span></td>
        </tr>
        {% endfor %}
    </tbody>
</table>
</div>
{% else %}
<div class="empty-state">No hay notificaciones.</div>
{% endif %}
{% else %}
<div class="stats">
    <div class="stat"><span class="stat-label">Consultas</span><span class="stat-value">{{ consultas_total }}</span></div>
    <div class="stat"><span class="stat-label">Respondidas</span><span class="stat-value" style="color:var(--green)">{{ consultas_respondidas }}</span></div>
</div>
<p style="color:var(--text2);margin-top:1.5rem;font-size:0.9rem;">
    Bienvenido, {{ user.name }}. Usa <a href="/dashboard/consulta" style="color:var(--accent);">Consultas</a> para enviar un mensaje.
</p>
{% endif %}
</div>
{% endblock %}
```

> **Qué hacer:** Reemplazar `<h2 style="...">` por un título con clase `.section-title` o similar. Quitar inline de `<p>` si se puede.

---

### 3. send.html (enviar)
```html
{% extends "base.html" %}
{% block title %}Enviar{% endblock %}
{% block content %}
<div class="main-header">
    <h1 class="main-title">Enviar notificacion</h1>
</div>
<div class="main-content">
<div style="display:grid;grid-template-columns:1fr 300px;gap:1.5rem;align-items:start;">
<div>
    <form method="post" action="/dashboard/send" class="form-card" style="max-width:100%;" id="sendForm">
        <div class="form-group">
            <label for="channel">Canal</label>
            <select id="channel" name="channel" required>
                <option value="email">Email</option>
                <option value="whatsapp">WhatsApp</option>
            </select>
        </div>
        <div class="form-group">
            <label for="user_id">Usuario</label>
            <select id="user_id" name="user_id">
                <option value="">— Sin asignar —</option>
                {% for u in users %}
                <option value="{{ u.id }}">{{ u.name }} ({{ u.email }})</option>
                {% endfor %}
            </select>
        </div>
        <div class="form-group">
            <label for="subject">Asunto</label>
            <input type="text" id="subject" name="subject" placeholder="Asunto del mensaje">
        </div>
        <div class="form-group">
            <label for="body">Mensaje</label>
            <textarea id="body" name="body" required placeholder="Contenido del mensaje..." rows="6"></textarea>
        </div>
        <button type="submit">Enviar</button>
    </form>
</div>
<div>
    <div class="form-card" style="max-width:100%;">
        <h3 style="font-size:0.85rem;font-weight:500;margin-bottom:0.75rem;color:var(--text2);">Consultas pendientes</h3>
        {% if pending_consultas %}
        <div style="display:flex;flex-direction:column;gap:0.5rem;">
            {% for c in pending_consultas %}
            <div class="consulta-pendiente" data-subject="{{ c.subject or '' }}" data-body="{{ c.message }}" data-user="{{ c.user.name if c.user else '' }}" style="padding:0.5rem;background:var(--bg);border-radius:6px;font-size:0.78rem;cursor:pointer;transition:background 0.15s;border:1px solid transparent;" onmouseover="this.style.borderColor='var(--accent)'" onmouseout="this.style.borderColor='transparent'" onclick="cargarConsulta(this)">
                <div style="color:var(--text2);">{{ c.created_at.strftime('%d/%m %H:%M') }} — {{ c.user.name if c.user else '?' }}</div>
                <div style="margin-top:0.2rem;">{{ c.subject or '(sin asunto)' }}</div>
            </div>
            {% endfor %}
        </div>
        {% else %}
        <div class="empty-state" style="padding:1rem;">Sin consultas pendientes</div>
        {% endif %}
    </div>
</div>
</div>
</div>
<script>
function cargarConsulta(el) {
    document.getElementById('subject').value = el.dataset.subject || '';
    document.getElementById('body').value = el.dataset.body || '';
    const userName = el.dataset.user;
    if (userName) {
        const sel = document.getElementById('user_id');
        for (let i = 0; i < sel.options.length; i++) {
            if (sel.options[i].text.startsWith(userName + ' (')) {
                sel.value = sel.options[i].value;
                break;
            }
        }
    }
}
</script>
{% endblock %}
```

> **Qué hacer:** Reemplazar todos los `style="..."` inline del panel derecho. Crear clase `.consulta-pendiente-item` en CSS o reusar `.consulta-item`. Quitar `onmouseover`/`onmouseout` y ponerlo en CSS con `:hover`.

---

### 4. history.html (historial)
```html
{% extends "base.html" %}
{% block title %}Historial{% endblock %}
{% block content %}
<div class="main-header">
    <h1 class="main-title">Historial</h1>
</div>
<div class="main-content">
<form method="get" action="/dashboard/history" class="filters" style="background:none;border:none;padding:0;max-width:100%;">
    <div class="form-group">
        <label for="channel">Canal</label>
        <select id="channel" name="channel">
            <option value="">Todos</option>
            <option value="email" {{ 'selected' if request.query_params.get('channel') == 'email' else '' }}>Email</option>
            <option value="whatsapp" {{ 'selected' if request.query_params.get('channel') == 'whatsapp' else '' }}>WhatsApp</option>
        </select>
    </div>
    <div class="form-group">
        <label for="status">Estado</label>
        <select id="status" name="status">
            <option value="">Todos</option>
            <option value="sent" {{ 'selected' if request.query_params.get('status') == 'sent' else '' }}>Enviado</option>
            <option value="pending" {{ 'selected' if request.query_params.get('status') == 'pending' else '' }}>Pendiente</option>
            <option value="failed" {{ 'selected' if request.query_params.get('status') == 'failed' else '' }}>Fallido</option>
        </select>
    </div>
    <button type="submit" class="btn" style="padding:0.45rem 1rem;font-size:0.82rem;">Filtrar</button>
    <a href="/dashboard/history" class="btn btn-secondary" style="padding:0.45rem 1rem;font-size:0.82rem;text-decoration:none;">Limpiar</a>
</form>
{% if notifications %}
<div class="table-container">
<table>
    <thead>
        <tr>
            <th>Fecha</th>
            <th>Canal</th>
            <th>Usuario</th>
            <th>Asunto</th>
            <th>Estado</th>
            <th>ID externo</th>
            <th>Error</th>
        </tr>
    </thead>
    <tbody>
        {% for n in notifications %}
        <tr>
            <td>{{ n.created_at.strftime('%d/%m %H:%M') }}</td>
            <td><span class="badge badge-{{ n.channel.value }}">{{ n.channel.value }}</span></td>
            <td>{{ n.user.name if n.user else '—' }}</td>
            <td>{{ n.subject or '(sin asunto)' }}</td>
            <td><span class="badge badge-{{ n.status.value }}">{{ n.status.value }}</span></td>
            <td style="font-size:0.75rem;color:var(--text2);">{{ n.external_id or '—' }}</td>
            <td style="font-size:0.75rem;color:var(--text2);">{{ n.error_message or '—' }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
</div>
{% if total_pages > 1 %}
<div class="pagination">
    {% if page > 1 %}
    <a href="?page={{ page - 1 }}{% if request.query_params.get('channel') %}&channel={{ request.query_params.get('channel') }}{% endif %}{% if request.query_params.get('status') %}&status={{ request.query_params.get('status') }}{% endif %}">← Anterior</a>
    {% endif %}
    <span class="current">{{ page }} / {{ total_pages }}</span>
    {% if page < total_pages %}
    <a href="?page={{ page + 1 }}{% if request.query_params.get('channel') %}&channel={{ request.query_params.get('channel') }}{% endif %}{% if request.query_params.get('status') %}&status={{ request.query_params.get('status') }}{% endif %}">Siguiente →</a>
    {% endif %}
</div>
{% endif %}
{% else %}
<div class="empty-state">No hay notificaciones con esos filtros.</div>
{% endif %}
</div>
{% endblock %}
```

> **Qué hacer:** Reemplazar `style="..."` inline en el form .filters, en los botones y en las celdas `td`. Crear clase `.cell-meta` para las celdas de ID externo y error.

---

### 5. templates.html (CRUD templates)
```html
{% extends "base.html" %}
{% block title %}Templates{% endblock %}
{% block content %}
<div class="main-header">
    <h1 class="main-title">Templates</h1>
</div>
<div class="main-content">
<div style="display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;align-items:start;">
<div>
<h2 style="font-size:1rem;font-weight:500;margin-bottom:0.75rem;">Nuevo template</h2>
<form method="post" action="/dashboard/templates" class="form-card" style="max-width:100%;">
    <div class="form-group">
        <label for="name">Nombre</label>
        <input type="text" id="name" name="name" required placeholder="ej: Bienvenida">
    </div>
    <div class="form-group">
        <label for="keywords">Keywords (separadas por coma)</label>
        <input type="text" id="keywords" name="keywords" required placeholder="ej: hola,buenos dias,consulta">
    </div>
    <div class="form-group">
        <label for="subject">Asunto (opcional)</label>
        <input type="text" id="subject" name="subject" placeholder="Asunto del template">
    </div>
    <div class="form-group">
        <label for="body">Cuerpo</label>
        <textarea id="body" name="body" required placeholder="Contenido del template..." rows="5"></textarea>
    </div>
    <button type="submit">Crear template</button>
</form>
</div>
<div>
<h2 style="font-size:1rem;font-weight:500;margin-bottom:0.75rem;">Templates existentes</h2>
{% if templates %}
<div style="display:flex;flex-direction:column;gap:0.5rem;">
    {% for t in templates %}
    <div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:0.75rem;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
                <strong style="font-size:0.9rem;">{{ t.name }}</strong>
                <span style="font-size:0.72rem;color:var(--text2);margin-left:0.5rem;">{{ t.keywords }}</span>
            </div>
            <form method="post" action="/dashboard/templates/{{ t.id }}/delete" style="margin:0;">
                <button type="submit" class="btn-danger" style="padding:0.25rem 0.6rem;font-size:0.75rem;" onclick="return confirm('Eliminar template?')">Eliminar</button>
            </form>
        </div>
        {% if t.subject %}<div style="font-size:0.8rem;color:var(--text2);margin-top:0.25rem;">{{ t.subject }}</div>{% endif %}
    </div>
    {% endfor %}
</div>
{% else %}
<div class="empty-state">No hay templates.</div>
{% endif %}
</div>
</div>
</div>
{% endblock %}
```

> **Qué hacer:** Reemplazar cards de templates inline por clase `.template-item` o `.card`. Reemplazar `<h2 style="...">` por clase.

---

### 6. users.html (CRUD usuarios)
```html
{% extends "base.html" %}
{% block title %}Usuarios{% endblock %}
{% block content %}
<div class="main-header">
    <h1 class="main-title">Usuarios</h1>
</div>
<div class="main-content">
<div style="display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;align-items:start;">
<div>
<h2 style="font-size:1rem;font-weight:500;margin-bottom:0.75rem;">Nuevo usuario</h2>
<form method="post" action="/dashboard/users" class="form-card" style="max-width:100%;">
    <div class="form-group">
        <label for="name">Nombre</label>
        <input type="text" id="name" name="name" required placeholder="Nombre completo">
    </div>
    <div class="form-group">
        <label for="email">Email</label>
        <input type="email" id="email" name="email" required placeholder="correo@ejemplo.com">
    </div>
    <div class="form-group">
        <label for="phone">WhatsApp</label>
        <input type="text" id="phone" name="phone" placeholder="5493875123456">
    </div>
    <button type="submit">Crear usuario</button>
</form>
</div>
<div>
<h2 style="font-size:1rem;font-weight:500;margin-bottom:0.75rem;">Usuarios registrados</h2>
{% if users %}
<div style="display:flex;flex-direction:column;gap:0.5rem;">
    {% for u in users %}
    <div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:0.75rem;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
                <strong style="font-size:0.9rem;">{{ u.name }}</strong>
                <div style="font-size:0.78rem;color:var(--text2);"> {{ u.email }} </div>
                {% if u.phone %}<div style="font-size:0.72rem;color:var(--text2);">{{ u.phone }}</div>{% endif %}
            </div>
            <form method="post" action="/dashboard/users/{{ u.id }}/delete" style="margin:0;">
                <button type="submit" class="btn-danger" style="padding:0.25rem 0.6rem;font-size:0.75rem;" onclick="return confirm('Eliminar {{ u.name }}?')">Eliminar</button>
            </form>
        </div>
    </div>
    {% endfor %}
</div>
{% else %}
<div class="empty-state">No hay usuarios.</div>
{% endif %}
</div>
</div>
</div>
{% endblock %}
```

> **Qué hacer:** Igual que templates — reemplazar cards inline por `.card` o `.user-item`. Reemplazar `<h2>` inline.

---

### 7. consulta.html (consultas — YA TIENE LA MAYORÍA DE CLASES)
```html
{% extends "base.html" %}
{% block title %}Consultas{% endblock %}
{% block content %}
<div class="main-header">
    <h1 class="main-title">Consultas</h1>
</div>
<div class="main-content">
<div style="display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;align-items:start;">
<div>
<h2 style="font-size:1rem;font-weight:500;margin-bottom:0.75rem;">Nueva consulta</h2>
<form method="post" action="/dashboard/consulta" class="form-card" style="max-width:100%;">
    <div class="form-group">
        <label for="subject">Asunto</label>
        <input type="text" id="subject" name="subject" required placeholder="Ej: Problema con mi pedido" maxlength="200">
    </div>
    <div class="form-group">
        <label for="message">Mensaje</label>
        <textarea id="message" name="message" required rows="5" placeholder="Describa su consulta..."></textarea>
    </div>
    <button type="submit">Enviar consulta</button>
</form>
</div>
<div>
<h2 style="font-size:1rem;font-weight:500;margin-bottom:0.75rem;">Historial</h2>
{% if consultas %}
<div style="display:flex;flex-direction:column;gap:0.5rem;">
    {% for c in consultas %}
    <div class="consulta-item">
        <div style="display:flex;justify-content:space-between;">
            <div class="subject">{{ c.subject }}</div>
            <div class="meta">{{ c.created_at.strftime('%d/%m %H:%M') }}</div>
        </div>
        <div class="meta">{{ c.message[:120] }}{% if c.message|length > 120 %}...{% endif %}</div>
        {% if c.response %}
        <div class="response-box">
            <strong style="font-size:0.78rem;color:var(--text2);">Respuesta:</strong>
            <div style="margin-top:0.25rem;">{{ c.response[:200] }}{% if c.response|length > 200 %}...{% endif %}</div>
            {% if c.responded_at %}<div style="font-size:0.7rem;color:var(--text2);margin-top:0.25rem;">{{ c.responded_at.strftime('%d/%m %H:%M') }}</div>{% endif %}
        </div>
        {% endif %}
    </div>
    {% endfor %}
</div>
{% else %}
<div class="empty-state">No tienes consultas.</div>
{% endif %}
</div>
</div>
</div>
{% endblock %}
```

> **Qué hacer:** Reemplazar `<h2>` y styles inline menores. Ya usa `.consulta-item` correctamente.

---

## Nuevas clases CSS a agregar en style.css

Además de reemplazar inline styles, agregar estas clases a `style.css`:

```css
/* Section title (reemplaza <h2> inline) */
.section-title {
    font-size: 1rem;
    font-weight: 500;
    margin-bottom: 0.75rem;
}

/* Item card for templates, users lists (reemplaza inline surface cards) */
.list-item {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.75rem;
}
.list-item-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* Pending consulta item in send.html sidebar */
.consulta-pendiente-item {
    padding: 0.5rem;
    background: var(--bg);
    border-radius: 6px;
    font-size: 0.78rem;
    cursor: pointer;
    transition: all 0.15s;
    border: 1px solid transparent;
}
.consulta-pendiente-item:hover {
    border-color: var(--accent);
}

/* Meta cell in tables (ID externo, error) */
.cell-meta {
    font-size: 0.75rem;
    color: var(--text2);
}

/* Welcome paragraph */
.welcome-text {
    color: var(--text2);
    margin-top: 1.5rem;
    font-size: 0.9rem;
}
.welcome-text a {
    color: var(--accent);
}

/* Pending consultas sidebar title */
.sidebar-title {
    font-size: 0.85rem;
    font-weight: 500;
    margin-bottom: 0.75rem;
    color: var(--text2);
}
```

---

## Output esperado

Devolver **7 archivos HTML** completos (base.html sin cambios + 6 transformados) con:
- Misma lógica Jinja2 intacta
- Clases CSS aplicadas, sin estilos inline
- Estética Linear: minimalista, bordes sutiles, Inter, OKLCH tokens
- Usar las nuevas clases `.section-title`, `.list-item`, `.list-item-header`, `.consulta-pendiente-item`, `.cell-meta`, `.welcome-text`, `.sidebar-title` donde corresponda
