# Guia de uso - Sistema de Notificaciones

## Escenario de prueba completo

### Datos ya creados en la DB

| Usuario | Email | Telefono | UUID |
|---------|-------|----------|------|
| Admin Desarrollador | admin@notificaciones.com | 5493875360385 | `aebcdb61-e248-4dee-91b4-ebcc1dc4cfce` |
| Juan Perez | juan@example.com | 5493875360386 | `21d39a17-8da3-4813-87a1-dd9f3441b181` |

### Templates ya creados

| Nombre | Keywords | Cuerpo |
|--------|----------|--------|
| saludo | hola, buenas | Hola! Como estas? |
| consulta | consulta, precio, informacion | Gracias por contactarnos... |

---

## Paso a paso

### 1. Abrir el Dashboard

http://localhost:8000/dashboard/

Ahi ves tarjetas con totales, ultimas notificaciones, y navegacion a las secciones.

### 2. Crear un usuario nuevo (opcional)

I a **Usuarios** → completar nombre, email, telefono → "Crear usuario".
El UUID se genera automaticamente, lo vas a necesitar despues.

### 3. Crear un template

I a **Templates** → completar:
- Nombre: `despedida`
- Keywords: `chau, gracias, adios`
- Asunto: `Gracias por contactarnos`
- Cuerpo: `Gracias por tu mensaje. Saludos!`

Esto se usa para el flujo automatico WhatsApp → Gmail.

### 4. Enviar una notificacion desde el dashboard

I a **Enviar** → completar:
- Canal: `Email`
- User ID: pegar el UUID de Admin (o dejar vacio)
- Asunto: `Hola mundo`
- Mensaje: `Este es un mensaje de prueba`
- Click "Enviar"

Aparece un mensaje verde con el ID de la notificacion.

### 5. Ver el historial

I a **Historial** → ahi estan todas las notificaciones.
Usar los filtros de canal y estado para acotar.

### 6. Probar el webhook de WhatsApp (simulado)

```powershell
Set-Content -Path "$env:TEMP\webhook.json" -Value '{"from":"5493875360385@c.us","body":"hola, necesito informacion","messageId":"test_001","timestamp":1700000000}'
curl.exe -s -X POST http://localhost:8000/whatsapp/webhook -H "Content-Type: application/json" -d "@$env:TEMP\webhook.json"
```

Esto activa el flujo automatico:
1. Detecta la keyword "hola" → matchea template "saludo"
2. Busca el usuario con telefono `5493875360385` → encuentra a Admin
3. Envia un email a `admin@notificaciones.com` con la respuesta del template

Verificarlo en el dashboard → Historial, deberia aparecer una notificacion "sent" con canal "email".

### 7. Probar el envio de WhatsApp real (si el bot esta conectado)

```powershell
curl.exe -s -X POST http://localhost:3001/send-message -H "Content-Type: application/json" -d '{\"to\":\"5493875360385@c.us\",\"message\":\"Hola desde el sistema\"}'
```

### 8. Probar la API directamente

```powershell
# Crear template
curl.exe -s -X POST http://localhost:8000/templates/ -H "Content-Type: application/json" -d '{\"name\":\"test_api\",\"keywords\":\"api,test\",\"body\":\"Template creado desde API\"}'

# Listar templates
curl.exe -s http://localhost:8000/templates/

# Enviar notificacion
curl.exe -s -X POST http://localhost:8000/notifications/send -H "Content-Type: application/json" -d '{\"channel\":\"email\",\"subject\":\"API test\",\"body\":\"Mensaje desde curl\"}'

# Ver historial
curl.exe -s http://localhost:8000/notifications/history
```

---

## Flujo integrado completo

```
1. Te llega un correo a la bandeja de Gmail configurada
       ↓
2. El polling (cada 30s) detecta el correo no leido
       ↓
3. Busca en la DB un usuario con ese email
       ↓
4. Si encuentra, reenvia el mensaje por WhatsApp al telefono del usuario
       ↓
5. El usuario responde por WhatsApp con una keyword (ej: "hola")
       ↓
6. El webhook /whatsapp/webhook recibe la respuesta
       ↓
7. Busca un template que coincida con la keyword
       ↓
8. Envia un email automatico al usuario con la respuesta del template
```

## Comandos utiles

```powershell
# Ver usuarios en DB
docker exec -i notificaciones-db psql -U user -d notificaciones -c "SELECT id, name, email, phone FROM users;"

# Ver logs del sistema
docker exec -i notificaciones-db psql -U user -d notificaciones -c "SELECT level, message, created_at FROM logs ORDER BY created_at DESC LIMIT 10;"

# Ver notificaciones recientes
docker exec -i notificaciones-db psql -U user -d notificaciones -c "SELECT channel, status, subject, created_at FROM notifications ORDER BY created_at DESC LIMIT 10;"

# Health check
curl.exe -s http://localhost:8000/health

# Ver templates
curl.exe -s http://localhost:8000/templates/

# Ejecutar tests
.venv\Scripts\pytest tests/ -v
```
