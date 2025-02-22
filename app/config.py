from dotenv import load_dotenv
from pydantic.v1 import BaseSettings

# Load environment variables from .env file
load_dotenv()


class Config(BaseSettings):
    VECTOR_DB_PORT: int
    VECTOR_DB_URI: str
    MONGO_URI: str
    COHERE_API_KEY: str
    MONGO_DB_NAME: str
    TAVILYAPI_KEY: str

    class Config:
        env_file = ".env"


config = Config()
