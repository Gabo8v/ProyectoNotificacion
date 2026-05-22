from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://user:password@localhost:5432/notificaciones"
    gmail_credentials_path: str = "credentials.json"
    gmail_token_path: str = "token.pickle"
    whatsapp_bot_url: str = "http://localhost:3001"

    class Config:
        env_file = ".env"


settings = Settings()
