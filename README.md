# Love Chat - MVP

Aplicación de chat con LLM y roleplay configurable. El backend (FastAPI) incluye autenticación con JWT, gestión de usuarios, personajes, conversaciones y streaming de respuestas del LLM.

## Estructura del proyecto

```
love_chat/
├── mvp-chat/
│   └── backend/          # API FastAPI (Python)
│       ├── app/
│       │   ├── admin/      # Panel admin (CRUD personajes, usuarios, métricas)
│       │   ├── auth/       # Autenticación (routes, schemas, security, deps)
│       │   ├── core/       # Config, DB, infraestructura
│       │   ├── models/     # Tablas SQLAlchemy (ORM)
│       │   ├── repos/      # Acceso a datos
│       │   ├── routes/     # Endpoints HTTP
│       │   ├── schemas/    # Modelos Pydantic (validación)
│       │   ├── services/   # Lógica de negocio, LLM, guardrails
│       │   └── main.py     # Punto de entrada FastAPI
│       ├── alembic/
│       ├── uploads/avatars/   # Avatares locales (usuarios y personajes)
│       ├── docker-compose.yml
│       ├── requirements.txt
│       └── .env.example
└── README.md
```

---

## Backend (MVP Chat)

### Requisitos

- Python 3.10+
- PostgreSQL 16
- Cuenta OpenAI (API key)

### Inicio rápido

1. **Clonar y entrar al backend:**
   ```bash
   cd love_chat/mvp-chat/backend
   ```

2. **Variables de entorno:**
   ```bash
   cp .env.example .env
   # Editar .env con tus valores (DATABASE_URL, OPENAI_API_KEY, JWT_SECRET, etc.)
   ```

3. **Levantar PostgreSQL con Docker:**
   ```bash
   docker-compose up -d
   ```

4. **Migraciones y servidor:**
   ```bash
   pip install -r requirements.txt
   alembic upgrade head
   uvicorn app.main:app --reload
   ```

La API estará en `http://localhost:8000`. Documentación interactiva: `http://localhost:8000/docs`.

---

## Arquitectura

```
Frontend → Routes (FastAPI) → Services → Repos → Postgres
                              ↓
                         LLM Client → OpenAI API
```

### Capas

| Capa | Ubicación | Responsabilidad |
|------|-----------|-----------------|
| **Routes** | `app/routes/`, `app/auth/` | Endpoints HTTP, validación de entrada |
| **Services** | `app/services/` | Lógica de negocio, prompts, guardrails, orquestación |
| **Repos** | `app/repos/` | Acceso a base de datos |
| **Models** | `app/models/` | Tablas SQLAlchemy (ORM) |
| **Schemas** | `app/schemas/` | Modelos Pydantic (validación request/response) |
| **Core** | `app/core/` | Config, conexión DB, infraestructura |

---

## API Endpoints

### Health
| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/health` | No | Estado del servicio |

### Auth
| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| POST | `/auth/register` | No | Registro (email, password, display_name, birthdate, gender) |
| POST | `/auth/login` | No | Login → access_token + refresh_token |
| POST | `/auth/refresh` | No | Renovar tokens con refresh_token |
| POST | `/auth/logout` | No | Revocar sesión (body: `{ "refresh_token": "..." }`) |

### Usuario
| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/me` | JWT | Perfil del usuario autenticado (incluye `avatar_url`) |
| PATCH | `/me/avatar` | JWT | Subir foto de perfil (multipart, campo `file`, jpg/png/webp, máx. 2 MB) |
| GET | `/me/usage` | JWT | Cuota diaria: unidades usadas, límite, restantes, reset_at |

### Personajes
| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/characters` | No | Lista de personajes (incluye `avatar_url`) |

### Conversaciones
| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/conversations` | JWT | Listar conversaciones del usuario (query: limit, offset) |
| POST | `/conversations` | JWT | Crear conversación con un personaje |
| POST | `/conversations/{id}/reset` | JWT | Cerrar y crear nueva conversación con el mismo personaje |

### Mensajes
| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| POST | `/conversations/{id}/messages` | JWT | Crear mensaje en la conversación |
| GET | `/conversations/{id}/messages` | JWT | Historial de mensajes (con limit) |

### Chat (streaming)
| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| POST | `/chat/stream` | JWT | Enviar mensaje y recibir respuesta en streaming (SSE). Body: `conversation_id`, `content`. Rate limit: 30 req/min. Cuota diaria por usuario (ver `/me/usage`). |

### Admin (header `X-Admin-Key`)
Requiere `ADMIN_SECRET` en `.env` y el header `X-Admin-Key: <valor>` en cada petición. Reiniciar el servidor tras añadir o cambiar `ADMIN_SECRET`.

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/admin/metrics` | Métricas: usuarios, personajes, conversaciones, mensajes |
| GET | `/admin/characters` | Listar personajes |
| POST | `/admin/characters` | Crear personaje |
| GET | `/admin/characters/{id}` | Obtener personaje |
| PATCH | `/admin/characters/{id}` | Actualizar personaje |
| DELETE | `/admin/characters/{id}` | Eliminar personaje (falla si tiene conversaciones) |
| GET | `/admin/users` | Listar usuarios (limit, offset) |
| GET | `/admin/users/{id}` | Obtener usuario |
| PATCH | `/admin/users/{id}/active` | Activar/desactivar usuario |

---

## Modelos de datos

### `users`
- `id` (UUID), `email`, `password_hash`, `is_active`, `created_at`

### `user_profiles`
- `user_id` (FK), `display_name`, `birthdate`, `gender`, `avatar_url`, `created_at`, `updated_at`

### `user_sessions`
- `id`, `user_id`, `refresh_jti`, `refresh_token_hash`, `created_at`, `expires_at`, `revoked_at`  
- Usado para rotación y revocación de refresh tokens

### `characters`
- `id`, `name`, `avatar_url`, `tone`, `dominance`, `affection`, `explicit_level`, `boundaries` (JSONB)

### `conversations`
- `id`, `character_id`, `user_id`, `status`, `created_at`

### `messages`
- `conversation_id`, `role` (user/assistant/system), `content`, timestamp

### `user_daily_usage`
- `user_id`, `date` (PK compuesta), `units_used`. Cuota diaria por usuario.

---

## Autenticación

- **Access token (JWT)**: corta duración (~30 min), se envía en `Authorization: Bearer <token>`
- **Refresh token**: larga duración (~30 días), para obtener nuevos access tokens
- **Registro**: crea `User` + `UserProfile` (display_name, birthdate, gender)
- **Login**: devuelve access + refresh; el refresh se almacena hasheado en `user_sessions`
- **Refresh**: revoca el token viejo y emite nuevos access + refresh
- **Logout**: `POST /auth/logout` con `refresh_token` en el body; revoca la sesión (idempotente)

---

## Servicios principales

### `chat_service.py`
- Valida guardrails (age gate 18+, bloqueos de contenido)
- Carga conversación, personaje y historial
- Construye system prompt con `prompt_builder`
- Llama al LLM vía `llm_client` (OpenAI Responses API)
- Stream de tokens y guardado de mensajes en DB

### `llm_client.py`
- Usa `openai.responses.create` con streaming
- Modelo configurable (`OPENAI_MODEL`, por defecto `gpt-4.1-mini`)

### `guardrails.py`
- Age gate 18+: se deriva de `birthdate` en `UserProfile` (no confía en el cliente). Sin birthdate o menor de 18 = denegado
- Bloqueo de menores y contenido no permitido
- Se ejecuta antes de llamar al LLM

### `prompt_builder.py`
- Genera el system prompt desde la config del personaje (sliders, tone, boundaries)

### `storage.py`
- Abstracción de almacenamiento: `LocalStorageBackend` (actual) y `S3StorageBackend` (futuro)
- Guarda avatares en `uploads/avatars/`, servidos en `/static/avatars/`

---

## Configuración (variables de entorno)

| Variable | Descripción |
|----------|-------------|
| `DATABASE_URL` | URL de PostgreSQL (ej: `postgresql+asyncpg://user:pass@localhost:5432/mvp_chat`) |
| `OPENAI_API_KEY` | API key de OpenAI |
| `OPENAI_MODEL` | Modelo a usar (default: `gpt-4.1-mini`) |
| `JWT_SECRET` | Secreto para firmar JWT |
| `JWT_ALGORITHM` | Algoritmo (default: `HS256`) |
| `ACCESS_TOKEN_EXP_MINUTES` | Caducidad del access token |
| `JWT_REFRESH_DAYS` | Caducidad del refresh token en días |
| `APP_NAME`, `APP_ENV`, `DEBUG`, `API_PREFIX` | Opcionales |
| `ADMIN_SECRET` | Opcional. Si se configura, habilita el panel admin (header `X-Admin-Key`) |
| `DAILY_UNITS_LIMIT` | Cuota diaria por usuario (default: 10000). 1 token de texto ≈ 1 unidad |
| `STORAGE_BACKEND` | `local` (actual) o `s3` (futuro) |
| `UPLOAD_DIR` | Carpeta para uploads locales (default: `uploads`) |
| `STATIC_URL_PREFIX` | Prefijo URL para servir archivos (default: `/static`) |

---

## Migraciones (Alembic)

```bash
alembic upgrade head    # Aplicar migraciones
alembic revision -m "descripción"   # Crear nueva migración
```

---

## Personajes por defecto

Al arrancar, si no hay personajes en la DB, se crean:

- **Luna**: tone `playful`, dominance 0.6, affection 0.8
- **Vera**: tone `romantic`, dominance 0.3, affection 0.9

Por defecto `avatar_url` es null. Para asignar fotos, coloca imágenes en `uploads/avatars/` y usa los curls de la sección [Storage (avatares)](#storage-avatares).

---

## Cuotas y rate limiting

- **Cuota diaria**: cada usuario tiene un límite de unidades/día (1 token ≈ 1 unidad). Configurable con `DAILY_UNITS_LIMIT`. Se actualiza tras cada respuesta del LLM.
- **Rate limit**: 30 requests/minuto en `/chat/stream` por usuario (JWT) o por IP.
- **`GET /me/usage`**: para mostrar en el frontend unidades usadas, límite, restantes y `reset_at`.
- **429**: cuando se supera la cuota o el rate limit.

Escalable: las unidades permiten sumar coste de imagen/audio en el futuro (p.ej. imagen = 500 unidades).

---

## Cómo cambiar límites y costos

### 1. Límite diario de tokens/unidades por usuario

**Archivo:** `app/core/config.py`  
**Variable de entorno:** `DAILY_UNITS_LIMIT`

| Cómo | Qué hacer |
|------|-----------|
| **Por .env** | Añadir `DAILY_UNITS_LIMIT=20000` en tu `.env` (sobrescribe el default) |
| **Default en código** | Cambiar `daily_units_limit: int = 10_000` en `app/core/config.py` |

Ejemplo: `DAILY_UNITS_LIMIT=5000` → cada usuario tiene 5 000 unidades/día.

---

### 2. Costo por mensaje (unidades por respuesta)

**Archivo:** `app/services/usage.py`  
**Función:** `estimate_text_units(text)`

Actualmente: ~4 caracteres ≈ 1 token ≈ 1 unidad.

| Qué quieres | Dónde | Cómo |
|-------------|-------|------|
| Cambiar relación chars/token | `usage.py` | Modificar `(len(text) + 3) // 4` (ej. `// 3` si ~3 chars/token) |
| Multiplicar costo (ej. 2x) | `usage.py` | Devolver `((len(text) + 3) // 4) * 2` |
| Sumar coste fijo por mensaje | `usage.py` o `chat_service.py` | Añadir constante extra a `units` antes de `UsageRepo.add_units` |

---

### 3. Rate limit (peticiones por minuto)

**Archivo:** `app/routes/chat.py`  
**Decorador:** `@limiter.limit("30/minute")`

| Qué cambiar | Dónde | Ejemplo |
|-------------|-------|---------|
| Peticiones por minuto | `chat.py` línea 21 | `@limiter.limit("60/minute")` |
| Por hora | `chat.py` | `@limiter.limit("100/hour")` |
| Por día | `chat.py` | `@limiter.limit("500/day")` |

---

### 4. Límites por usuario/plan (futuro)

Hoy todos los usuarios comparten el mismo `DAILY_UNITS_LIMIT`. Para límites distintos por usuario o plan:

1. Crear tabla `user_limits` (user_id, daily_units_limit, etc.).
2. Modificar `app/core/config.py` para usar límite por usuario si existe, si no el global.
3. Modificar `ChatService` y `UsageRepo` para leer el límite del usuario en vez del config.

---

### Resumen de archivos

| Qué | Archivo | Variable/Ubicación |
|-----|---------|--------------------|
| Límite diario global | `app/core/config.py` | `daily_units_limit` / `DAILY_UNITS_LIMIT` |
| Cálculo unidades por texto | `app/services/usage.py` | `estimate_text_units()` |
| Rate limit chat | `app/routes/chat.py` | `@limiter.limit("30/minute")` |
| Actualización de cuota | `app/services/chat_service.py` | Llamada a `UsageRepo.add_units` tras cada respuesta |

---

## Storage (avatares)

- **Actual**: almacenamiento local en `uploads/avatars/`. Archivos servidos en `/static/avatars/`.
- **S3 (futuro)**: configurar `STORAGE_BACKEND=s3` y completar `S3StorageBackend` en `app/services/storage.py` con boto3 (S3_BUCKET, S3_REGION, etc.).
- **Usuarios**: `PATCH /me/avatar` sube foto; el usuario puede cambiarla.
- **Personajes**: `avatar_url` se define en admin o seed; el usuario no la modifica.

Para asignar avatares a Luna y Vera (tras colocar las imágenes en `uploads/avatars/`):

```bash
cd love_chat/mvp-chat/backend

# Cargar solo ADMIN_SECRET (más fiable que export del .env completo)
ADMIN_SECRET=$(grep '^ADMIN_SECRET=' .env | cut -d= -f2-)

# Luna
curl -X PATCH "http://localhost:8000/admin/characters/luna" \
  -H "X-Admin-Key: $ADMIN_SECRET" \
  -H "Content-Type: application/json" \
  -d '{"avatar_url": "http://localhost:8000/static/avatars/Luna.jpg"}'

# Vera
curl -X PATCH "http://localhost:8000/admin/characters/vera" \
  -H "X-Admin-Key: $ADMIN_SECRET" \
  -H "Content-Type: application/json" \
  -d '{"avatar_url": "http://localhost:8000/static/avatars/Vera.jpg"}'
```

O usando el valor directamente (reemplaza `tu-secreto-admin-muy-largo` por tu `ADMIN_SECRET`):

```bash
# Luna
curl -X PATCH "http://localhost:8000/admin/characters/luna" \
  -H "X-Admin-Key: tu-secreto-admin-muy-largo" \
  -H "Content-Type: application/json" \
  -d '{"avatar_url": "http://localhost:8000/static/avatars/Luna.jpg"}'

# Vera
curl -X PATCH "http://localhost:8000/admin/characters/vera" \
  -H "X-Admin-Key: tu-secreto-admin-muy-largo" \
  -H "Content-Type: application/json" \
  -d '{"avatar_url": "http://localhost:8000/static/avatars/Vera.jpg"}'
```

---

## Próximos pasos (crecimiento)

- Límites por plan / suscripción
- Memoria larga (tabla `memory` + embeddings)
- Pagos y límites por plan
- Cambio de proveedor LLM sin tocar el resto (solo `llm_client.py`)
- Migración a S3 para storage de avatares