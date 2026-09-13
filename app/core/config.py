import os
from functools import lru_cache
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Locate project root and load .env
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"
if ENV_FILE.exists():
    load_dotenv(dotenv_path=ENV_FILE)
else:
    load_dotenv()


class Settings:
    PROJECT_NAME: str = "India MSME Scheme Recommendation Platform API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8080"))

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./goi_schemes.db",
    )
    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "10"))
    DATABASE_SSL: bool = os.getenv("DATABASE_SSL", "false").lower() in ("true", "1")

    # JWT Authentication
    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY",
        "development_jwt_secret_key_msme_recommendation_platform_2026_super_secure_key",
    )
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    REFRESH_TOKEN_SECRET: str = os.getenv("REFRESH_TOKEN_SECRET", "development_refresh_token_secret")
    REFRESH_TOKEN_EXPIRY_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRY_DAYS", "30"))

    # CORS settings (comma-separated list of allowed origins)
    _cors_origins_env: str = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173",
    )

    # Server-Side Anthropic Claude API Key for Qualitative Market Intelligence & DPR
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    CLAUDE_MODEL: str = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
    CLAUDE_MAX_TOKENS: int = int(os.getenv("CLAUDE_MAX_TOKENS", "2000"))

    # Redis Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # AWS / S3 Configuration
    AWS_REGION: str = os.getenv("AWS_REGION", "ap-south-1")
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_S3_BUCKET: str = os.getenv("AWS_S3_BUCKET", "sih26091-reports")

    # Rate Limiting
    RATE_LIMIT_WINDOW_MS: int = int(os.getenv("RATE_LIMIT_WINDOW_MS", "900000"))
    RATE_LIMIT_MAX_REQUESTS: int = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "100"))

    # Feature Toggles
    FEATURE_CHAT_ENABLED: bool = os.getenv("FEATURE_CHAT_ENABLED", "true").lower() in ("true", "1")
    FEATURE_OFFLINE_MODE: bool = os.getenv("FEATURE_OFFLINE_MODE", "true").lower() in ("true", "1")
    FEATURE_SCHEME_VECTOR_SEARCH: bool = os.getenv("FEATURE_SCHEME_VECTOR_SEARCH", "true").lower() in ("true", "1")
    FEATURE_PDF_GENERATION: bool = os.getenv("FEATURE_PDF_GENERATION", "true").lower() in ("true", "1")

    # Sentry DSN
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")

    if not ANTHROPIC_API_KEY:
        # Check local frontend .env if present during unified local development
        _fe_env = BASE_DIR / "frontend" / ".env"
        if _fe_env.exists():
            load_dotenv(dotenv_path=_fe_env, override=False)
            ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

    @property
    def CORS_ORIGINS(self) -> List[str]:
        if not self._cors_origins_env:
            return ["*"]
        return [origin.strip() for origin in self._cors_origins_env.split(",") if origin.strip()]

    def __repr__(self) -> str:
        # Prevent credential leakage
        return f"<Settings project={self.PROJECT_NAME} env={self.ENVIRONMENT}>"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
