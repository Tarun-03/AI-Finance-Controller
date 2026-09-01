from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str

    # LLM configuration
    LLM_PROVIDER: str = "none"
    LLM_MODEL: str = ""

    # Keep API key optional for now.
    LLM_API_KEY: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()