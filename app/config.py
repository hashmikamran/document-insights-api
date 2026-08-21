from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "document_insights"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    CACHE_TTL_SECONDS: int = 86400
    MAX_ACTIVE_JOBS_PER_USER: int = 3

    class Config:
        env_file = ".env"

settings = Settings()