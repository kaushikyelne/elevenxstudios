from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:root@localhost:5432/moneylane"
    
    class Config:
        env_file = ".env"

settings = Settings()
