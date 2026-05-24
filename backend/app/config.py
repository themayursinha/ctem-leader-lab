from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://ctem:ctem@localhost:5432/ctem"
    cors_origins: list[str] = [
        "http://localhost:5173", "http://localhost:5174", "http://localhost:5175",
        "http://127.0.0.1:5173", "http://127.0.0.1:5174", "http://127.0.0.1:5175",
        "http://localhost:8080",
    ]
    admin_token: str | None = None
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440
    debug: bool = False

    model_config = {"env_prefix": "ctem_", "env_file": ".env"}


settings = Settings()
