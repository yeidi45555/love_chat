from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "MVP Chat Backend"
    app_env: str = "local"
    debug: bool = False
    api_prefix: str = ""

    database_url: str
    openai_model: str = "gpt-4.1-mini"
    openai_api_key: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_exp_minutes: int = 30
    jwt_refresh_days: int = 30

    admin_secret: str | None = None  # Si está configurado, habilita el panel admin (header X-Admin-Key)

    daily_units_limit: int = 1000  # Cuota diaria por usuario (1 token ≈ 1 unidad)

    # Storage: local | s3 (s3 para futuro)
    storage_backend: str = "local"
    upload_dir: str = "uploads"
    static_url_prefix: str = "/static"
    # Para S3 (cuando se use):
    # s3_bucket: str | None = None
    # s3_region: str | None = None
    # s3_endpoint_url: str | None = None


settings = Settings()
