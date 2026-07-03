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
    REDIS_HOST: str
    REDIS_PORT: int

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()  # type: ignore
