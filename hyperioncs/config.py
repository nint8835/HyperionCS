from dotenv import load_dotenv
from pydantic import BaseSettings


class Config(BaseSettings):
    secret_key: str = "top-secret-key"
    discord_client_id: str
    discord_client_secret: str


load_dotenv()
config = Config()
