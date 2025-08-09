from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="hyperion_", env_file=".env")

    log_level: str = "INFO"
    is_production: bool = False
    session_secret: str

    client_id: str
    client_secret: str

    bind_host: str = "0.0.0.0"
    bind_port: int = 8000
    behind_reverse_proxy: bool = False

    db_path: str = "hyperion.sqlite"
    db_log_queries: bool = False

    @property
    def async_db_connection_uri(self) -> str:
        return f"sqlite+aiosqlite:///{self.db_path}"

    @property
    def sync_db_connection_uri(self) -> str:
        return f"sqlite:///{self.db_path}"


config = Config()  # type: ignore - Pyright doesn't know about pydantic_settings
