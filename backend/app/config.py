from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "postgres"
    db_password: str = 1111
    db_name: str = "umax_crm"

    secret_key: str = "umax_super_secret_key_change_me_2024"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480
    app_name: str = "Umax CRM"
    app_version: str = "1.0.0"
    debug: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    def connection_params(self) -> dict:
        return {
            "host": self.db_host,
            "port": self.db_port,
            "user": self.db_user,
            "password": self.db_password,
            "dbname": self.db_name,
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
