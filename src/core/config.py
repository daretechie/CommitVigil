# Copyright (c) 2026 CommitVigil AI. All rights reserved.
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    PROJECT_NAME: str = "CommitVigil"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    LOG_LEVEL: str = "INFO"  # Options: DEBUG, INFO, WARNING, ERROR

    # AI Config
    OPENAI_API_KEY: str = Field(..., description="OpenAI API Key must be provided")
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
    DB_PATH: str = "commitvigil.db"  # Legacy support
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/commitvigil"
    SYNC_DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/commitvigil"

    # Integrations
    SLACK_WEBHOOK_URL: str | None = None

    # Roadmap: Multi-Language & Industry
    SUPPORTED_LANGUAGES: dict[str, str] = {
        "en": "English (Global)",
        "en-UK": "English (British idioms)",
        "en-AF": "English (African communal accountability)",
        "ja": "Japanese (High-context culture)",
        "de": "German (Direct communication style)",
    }
    SELECTED_INDUSTRY: str = "generic"  # Options: generic, healthcare, finance
    LEARNING_ENABLED: bool = True

    # Security

    # Security
    # Security
    # Security
    API_KEY_SECRET: str = Field(..., min_length=16)  # Forced override in all environments
    AUTH_ENABLED: bool = True  # Feature Flag for Dev Mode
    DEMO_MODE: bool = False  # If True, enables mock fallbacks and sync execution

    # Default to localhost only for development; Production MUST override this via env var
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Operational Timings
    FOLLOW_UP_DELAY_SECONDS: int = 10
    LATENCY_SLA_THRESHOLD_MS: int = 500

    # Sales Intelligence & ROI Assumptions
    ROI_WORKING_HOURS_PER_YEAR: int = 2000
    ROI_IMPROVEMENT_FACTOR: float = 0.40
    ROI_MONTHLY_FEE_USD: float = 500.0

    # For local development
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
