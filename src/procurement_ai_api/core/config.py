from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MONGO_URI: str
    DB_NAME: str
    
    OPENAI_API_KEY: str

    MAX_RETRIES: int = 2
    MAX_HISTORY_MESSAGES: int = 10

    AI_MODEL: str 

    FRONTEND_URL: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()