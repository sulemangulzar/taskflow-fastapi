from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    DEBUG: bool = False
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_ISSUER: str
    JWT_AUDIENCE: str
    REFRESH_TOKEN_EXPIRE_DAYS: int
    REDIS_URL: str
    REDIS_HOST: str
    REDIS_PORT: int
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_SERVER: str
    MAIL_PORT: int
    DOMAIN: str
    FRONTEND_ORIGINS: str = "http://localhost:5173"
    CORS_ORIGIN_REGEX: str | None = r"https://.*\\.vercel\\.app"
    ALLOWED_HOSTS: str = "localhost,127.0.0.1,test,testserver,*.onrender.com"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+asyncpg://", 1)
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+asyncpg://", 1)
        return value

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()  # type: ignore

broker_url = settings.REDIS_URL
result_backend = settings.REDIS_URL
