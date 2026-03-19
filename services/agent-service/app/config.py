from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-1.5-flash"
    notification_service_url: str | None = None
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
