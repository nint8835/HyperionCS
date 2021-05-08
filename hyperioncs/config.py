from dotenv import load_dotenv
from pydantic import BaseSettings


class Config(BaseSettings):
    secret_key: str = "top-secret-key"
    jwt_secret_key: str = "really-secret-key"
    jwt_algorithm: str = "HS256"
    discord_client_id: str
    discord_client_secret: str
    sqlalchemy_connection_url: str = "postgresql://hyperion:hyperion@localhost/hyperion"


load_dotenv()
config = Config()
