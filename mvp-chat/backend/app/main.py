from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.db import engine
from app.core.rate_limit import limiter
from app.models import Base
from app.routes import health_router, characters_router, conversations_router, messages_router, chat_router
from app.auth.routes import router as auth_router
from app.routes import me_router
from app.admin.routes import router as admin_router
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware

from sqlalchemy import select
from app.core.db import AsyncSessionLocal
from app.models import Character

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    version="0.1.0",
)

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(characters_router, prefix=settings.api_prefix)
app.include_router(conversations_router, prefix=settings.api_prefix)
app.include_router(messages_router, prefix=settings.api_prefix)
app.include_router(chat_router, prefix=settings.api_prefix)
app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(me_router, prefix=settings.api_prefix)
app.include_router(admin_router, prefix=settings.api_prefix)

# Static files (avatars locales)
upload_dir = Path(settings.upload_dir)
upload_dir.mkdir(exist_ok=True)
(upload_dir / "avatars").mkdir(exist_ok=True)
app.mount(settings.static_url_prefix, StaticFiles(directory=str(upload_dir)), name="static")

@app.on_event("startup")
async def on_startup():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Character))
        exists = result.scalars().first()
        if exists:
            return

        session.add_all([
            Character(
                id="luna",
                name="Luna",
                avatar_url=None,
                tone="playful",
                dominance=0.6,
                affection=0.8,
                explicit_level=0.5,
                boundaries=["no minors", "no incest", "no violence", "no illegal content"],
            ),
            Character(
                id="vera",
                name="Vera",
                avatar_url=None,
                tone="romantic",
                dominance=0.3,
                affection=0.9,
                explicit_level=0.4,
                boundaries=["no minors", "no incest", "no violence", "no illegal content"],
            ),
        ])
        await session.commit()