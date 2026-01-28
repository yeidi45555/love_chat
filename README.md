# MVP Chat Backend (Base para la app final)

Este backend es la base del MVP de una aplicación de chat con LLM y roleplay configurable.
El objetivo del MVP es:
1) Servir una lista de personajes configurables
2) Crear conversaciones por personaje
3) Guardar historial de mensajes
4) Enviar mensajes al LLM (más adelante) con control de prompt y guardrails
5) Responder en streaming (para que el frontend muestre “typing”)

---

## Arquitectura (capas)

El flujo principal es:

Frontend → **Routes (FastAPI)** → **Services (lógica)** → **Repos (DB)** → Postgres  
y Services → **LLM Client** → proveedor LLM (API externa)

Capas:
- **routes/**: endpoints HTTP (entrada/salida)
- **services/**: lógica de negocio (prompt, guardrails, orquestación)
- **repos/**: acceso a base de datos (consultas)
- **models/**: tablas SQLAlchemy (estructura DB)
- **schemas/**: modelos Pydantic (validación request/response)
- **core/**: config y conexión a DB (infraestructura)

---

## Estructura de carpetas y archivos

### `app/`
Contiene el código principal de la API (FastAPI). Es el “paquete” de la aplicación.

#### `app/main.py`
- Crea la instancia de `FastAPI`
- Registra routers (`routes/`)
- Define eventos de startup/shutdown (si aplica)
- Punto de entrada para correr la API:
  - `uvicorn app.main:app --reload`

#### `app/__init__.py`
- Marca `app/` como módulo importable.

---

### `app/core/` (Infraestructura)
Código compartido que usan todas las capas.

#### `app/core/config.py`
- Maneja configuración por variables de entorno:
  - `DATABASE_URL`
  - `APP_ENV`
- Centraliza settings para no hardcodear valores.

#### `app/core/db.py`
- Crea el engine async de SQLAlchemy
- Define la factory de sesiones (`AsyncSession`)
- Expone un dependency para FastAPI (`get_db`) usado en routes.

---

### `app/models/` (Tablas / ORM)
Define cómo se ve la base de datos.

#### `app/models/base.py`
- Contiene la clase `Base` (DeclarativeBase) que heredan los modelos.

#### `app/models/character.py`
Tabla `characters`
- Guarda los personajes (presets)
- Campos típicos:
  - `id`, `name`
  - sliders: `dominance`, `affection`, `explicit_level`
  - `tone`
  - `boundaries`

#### `app/models/conversation.py`
Tabla `conversations`
- Una conversación está asociada a un personaje.
- Campos típicos:
  - `id`
  - `character_id`
  - timestamps

#### `app/models/message.py`
Tabla `messages`
- Historial de mensajes por conversación
- Campos típicos:
  - `conversation_id`
  - `role` (user/assistant/system)
  - `content`
  - timestamp

#### `app/models/__init__.py`
- Exporta modelos para imports más limpios.

---

### `app/schemas/` (Pydantic: contratos de API)
Define los modelos de entrada/salida del API (DTOs).

#### `app/schemas/character.py`
- `CharacterOut`: lo que devuelve `GET /characters`
- `CharacterCreate` (si decides crear personajes por API en el futuro)

#### `app/schemas/conversation.py`
- `ConversationCreate`: body para crear conversación
- `ConversationOut`: respuesta al crear conversación

#### `app/schemas/message.py`
- `SendMessageIn`: body para enviar un mensaje
- `MessageOut`: modelo de respuesta para mensajes

---

### `app/repos/` (Acceso a datos)
Los repositorios son funciones/clases que hacen queries a la DB.
Esto evita que la lógica SQL se mezcle con services.

#### `app/repos/character_repo.py`
- Listar personajes
- Obtener personaje por id
- Insert/update (si aplica)

#### `app/repos/conversation_repo.py`
- Crear conversación
- Obtener conversación por id

#### `app/repos/message_repo.py`
- Insertar mensaje
- Obtener últimos N mensajes (memoria corta)

---

### `app/services/` (Lógica de negocio)
Aquí vive el “cerebro” del MVP.

#### `app/services/guardrails.py`
- Reglas mínimas de seguridad y políticas:
  - age gate 18+
  - bloqueo estricto de menores
  - bloqueos básicos de contenido no permitido
- Importante: esto corre ANTES de llamar al LLM.

#### `app/services/prompt_builder.py`
- Construye el `system prompt` a partir de `CharacterConfig`
- Convierte sliders + tone + boundaries en instrucciones de roleplay.
- Nota: el usuario NO debe escribir prompts libres; se generan desde config.

#### `app/services/llm_client.py`
- Encapsula el proveedor LLM (API externa)
- Para MVP puede iniciar como “stub” (simulación)
- Luego se reemplaza por streaming real sin cambiar el resto del sistema.

#### `app/services/chat_service.py`
- Orquestador del chat:
  - valida guardrails
  - carga conversación y personaje
  - arma prompt
  - carga historial (últimos N mensajes)
  - llama al LLM
  - stream de tokens
  - guarda mensajes en DB

---

### `app/routes/` (EndPoints FastAPI)
Solo reciben requests y devuelven responses. Casi sin lógica.

#### `app/routes/characters.py`
- `GET /characters`
- Devuelve presets de personajes

#### `app/routes/conversations.py`
- `POST /conversations`
- Crea conversación con un personaje

#### `app/routes/chat.py`
- `POST /chat/stream`
- Envía mensaje y devuelve respuesta en streaming (SSE)

#### `app/routes/__init__.py`
- Re-exporta routers para importarlos en `main.py`

---

## Migraciones

### `alembic/`
- Configuración de migraciones.
- `versions/` contiene los archivos de migración.

### `alembic.ini`
- Config global de Alembic (path, logging, etc.)

---

## Archivos de entorno y dependencias

### `requirements.txt`
- Dependencias versionadas para reproducibilidad

### `.env.example`
- Plantilla con variables necesarias (sin secretos reales)

---

## Cómo crecer desde este MVP a la app final
Este MVP está diseñado para crecer sin reescribir:
- Añadir Auth (users, JWT) sin tocar services centrales
- Añadir pagos y límites por plan (rate limiting por usuario)
- Añadir memoria larga (tabla “memory” + embeddings si se requiere)
- Añadir panel admin para crear personajes
- Cambiar el proveedor LLM sin cambiar routes (solo `llm_client.py`)
