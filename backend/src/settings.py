from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SERVER_ADDR: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    SERVER_TEST: bool = True
    SERVER_WORKERS: int = 1

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_ADDR: str = "db"
    POSTGRES_PORT: int = 5432

    AWS_HOST: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_BUCKET: str
    AWS_REGION: str = "us-east-1"

    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_USER: str
    RABBITMQ_PASS: str
    RABBITMQ_PORT: int = 5672

    CHROMADB_URL: str = "your-chromadb-url"
    CHROMADB_PORT: int = 8001
    CHROMADB_NAME: str = "towers"


settings = Settings()
