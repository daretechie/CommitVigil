from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "CommitGuard AI"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    LOG_LEVEL: str = "INFO"  # Options: DEBUG, INFO, WARNING, ERROR

    # AI Config
    OPENAI_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None
    MODEL_NAME: str = "gpt-4o"
    LLM_PROVIDER: str = "openai"  # Options: openai, groq, mock

    # Ethical & Sensitivity Settings
    CULTURAL_DIRECTNESS_LEVEL: str = "high"  # Options: low, medium, high
    COOLING_OFF_PERIOD_HOURS: int = 48
    MIN_AI_CONFIDENCE_THRESHOLD: float = 0.75
    SAFETY_CONFIDENCE_THRESHOLD: float = 0.8
    MAX_INPUT_CHARS: int = 15000  # Token safety limit

    # Infrastructure
    REDIS_URL: str = "redis://localhost:6380"
    DB_PATH: str = "commitguard.db"  # Legacy support
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/commitguard"

    # Integrations
    SLACK_WEBHOOK_URL: str | None = None

    # Roadmap: Multi-Language & Industry
    SUPPORTED_LANGUAGES: dict[str, str] = {
        "en": "English (Global)",
        "en-UK": "English (British idioms)",
        "ja": "Japanese (High-context culture)",
        "de": "German (Direct communication style)",
    }
    SELECTED_INDUSTRY: str = "generic"  # Options: generic, healthcare, finance
    LEARNING_ENABLED: bool = True

    # Security

    # Security
    API_KEY_SECRET: str = "dev-secret-key"  # Default for dev; Override in Prod!
    AUTH_ENABLED: bool = True  # Feature Flag for Dev Mode

    # Default to localhost only for development; Production MUST override this via env var
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Operational Timings
    FOLLOW_UP_DELAY_SECONDS: int = 10
    LATENCY_SLA_THRESHOLD_MS: int = 500

    # For local development
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
