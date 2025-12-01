from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_ENV: str = "production"

    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    FRONTEND_URL: str
    BACKEND_URL: str
    OWNER_MODE: bool = True

    # AI Keys
    GEMINI_API_KEY: str
    OPENAI_API_KEY: str | None = None

    # Cloudflare R2
    CLOUDFLARE_ACCOUNT_ID: str
    CLOUDFLARE_R2_ACCESS_KEY: str
    CLOUDFLARE_R2_SECRET_KEY: str
    CLOUDFLARE_R2_BUCKET: str

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

if "postgres" in settings.DATABASE_URL and "sslmode" not in settings.DATABASE_URL:
    settings.DATABASE_URL += "?sslmode=require"
