from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_ADDR: str = "db"
    POSTGRES_PORT: int = 5432

    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_USER: str = "quest"
    RABBITMQ_PASS: str = "quest"
    RABBITMQ_PORT: int = 5672

    AWS_HOST: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_BUCKET: str
    AWS_REGION: str = "us-east-1"

    MODEL: int = 0
    WEIGHTS_DIR: str = "../weights"


settings = Settings()
