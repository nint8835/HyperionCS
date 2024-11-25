from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    secret_key: str = "top-secret-key"
    jwt_secret_key: str = "really-secret-key"
    jwt_algorithm: str = "HS256"
    discord_client_id: str
    discord_client_secret: str
    sqlalchemy_connection_url: str = "sqlite:///hyperion.sqlite"


config = Config()  # type: ignore - Pyright doesn't know about pydantic_settings

__all__ = ["config"]
