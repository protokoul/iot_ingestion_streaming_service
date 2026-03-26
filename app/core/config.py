from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="IoT Data Ingestion & Streaming Service", alias="APP_NAME")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    api_v1_prefix: str = Field(default="", alias="API_V1_PREFIX")
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    jwt_secret_key: str = Field(alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(default=60, alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")

    mongo_uri: str = Field(alias="MONGO_URI")
    mongo_db_name: str = Field(default="iot_service", alias="MONGO_DB_NAME")

    redis_url: str = Field(alias="REDIS_URL")
    redis_channel_prefix: str = Field(default="iot:user:", alias="REDIS_CHANNEL_PREFIX")

    bootstrap_admin_username: str = Field(default="admin", alias="BOOTSTRAP_ADMIN_USERNAME")
    bootstrap_admin_password: str = Field(default="password", alias="BOOTSTRAP_ADMIN_PASSWORD")


@lru_cache
def get_settings() -> Settings:
    return Settings()
