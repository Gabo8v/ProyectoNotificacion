from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://user:password@localhost:5432/notificaciones"
    gmail_credentials_path: str = "credentials.json"
    gmail_token_path: str = "token.pickle"
    whatsapp_bot_url: str = "http://localhost:3001"
    admin_username: str = "admin"
    admin_password: str = "admin123"
    token_encryption_key: str = ""
    cors_origins: str = "http://localhost:8000,http://127.0.0.1:8000"
    webhook_api_key: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
