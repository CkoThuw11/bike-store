from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE_CONFIG = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
    extra="ignore",
)


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(**_ENV_FILE_CONFIG, env_prefix="DATABASE_")

    host: str
    port: int
    name: str
    user: str
    password: str
    pool_size: int = Field(default=20)
    max_overflow: int = Field(default=10)

    @property
    def url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
        )


class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(**_ENV_FILE_CONFIG, env_prefix="AUTH_")

    secret_key: str
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=15)
    refresh_token_expire_days: int = Field(default=7)


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(**_ENV_FILE_CONFIG, env_prefix="APP_")

    debug: bool = Field(default=True)
    cors_origins: list[str] = Field(default=["http://localhost:3000"])
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    log_format: str = Field(default="text", validation_alias="LOG_FORMAT")


class Settings(BaseSettings):
    model_config = _ENV_FILE_CONFIG

    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    auth: AuthSettings = Field(default_factory=AuthSettings)
    app: AppSettings = Field(default_factory=AppSettings)


settings = Settings()
