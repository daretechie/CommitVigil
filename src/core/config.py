from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "CommitGuard AI"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # AI Config
    OPENAI_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None
    MODEL_NAME: str = "gpt-4o"
    LLM_PROVIDER: str = "openai"  # Options: openai, groq, mock

    # Infrastructure
    REDIS_URL: str = "redis://localhost:6380"
    DB_PATH: str = "commitguard.db" # Legacy support
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/commitguard"


    # Integrations
    SLACK_WEBHOOK_URL: str | None = None

    # Security

    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    # Operational Timings
    FOLLOW_UP_DELAY_SECONDS: int = 10

    # For local development
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
