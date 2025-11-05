from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "OmniAI Studio Universe API"
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    DATABASE_URL: str = "postgresql://omni:omni_pass@localhost:5432/omni_core"

    JWT_SECRET_KEY: str = "replace-this-in-.env"
    JWT_REFRESH_SECRET_KEY: str = "replace-this-refresh-in-.env"
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    class Config:
        env_file = ".env"

settings = Settings()
