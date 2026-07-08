from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

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
    REDIS_HOST: str = ""
    REDIS_PORT: int = 6379
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
        if not isinstance(value, str):
            return value

        normalized = value.strip()
        if normalized.startswith("postgres://"):
            normalized = normalized.replace("postgres://", "postgresql+asyncpg://", 1)
        elif normalized.startswith("postgresql://"):
            normalized = normalized.replace("postgresql://", "postgresql+asyncpg://", 1)

        if normalized.startswith("postgresql+asyncpg://"):
            parts = urlsplit(normalized)
            query = dict(parse_qsl(parts.query, keep_blank_values=True))

            query.pop("channel_binding", None)

            ssl_value = query.pop("ssl", None)
            if ssl_value and ssl_value.lower() in {"true", "1", "yes"}:
                query.setdefault("sslmode", "require")

            normalized = urlunsplit(
                (
                    parts.scheme,
                    parts.netloc,
                    parts.path,
                    urlencode(query),
                    parts.fragment,
                )
            )

        return normalized

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()  # type: ignore

broker_url = settings.REDIS_URL
result_backend = settings.REDIS_URL
