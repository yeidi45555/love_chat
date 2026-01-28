from fastapi import FastAPI
from app.routes import health_router

app = FastAPI(
    title="MVP Chat Backend",
    version="0.1.0"
)

app.include_router(health_router)
