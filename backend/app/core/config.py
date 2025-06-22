"""
Centralised application configuration.

Everything is derived from environment variables via Pydantic’s `BaseSettings`.
Any setting can be overridden by exporting an environment variable of the
same name **before** the app starts (or by adding it to your `.env` file).

Usage
-----
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, ...)
"""

from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic import (
    AnyHttpUrl,
    AnyUrl,
    BaseSettings,
    Field,
    PostgresDsn,
    validator,
)


class Settings(BaseSettings):
    # ›——————————————————  General  ——————————————————‹
    APP_NAME: str = "Scheduler API"
    APP_ENV: str = Field(
        default="dev",
        description="Environment flag: dev | staging | prod",
    )
    DEBUG: bool = Field(default=True, description="Enable verbose error pages")
    LOG_LEVEL: str = Field(default="INFO", description="root logger level")

    # ›——————————————————  Hosts / CORS  ——————————————————‹
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:5173",
    ]

    # ›——————————————————  Database  ——————————————————‹
    DATABASE_URL: PostgresDsn | AnyUrl | str = Field(
        default="sqlite:///./dev.db",
        description="SQLAlchemy URL",
    )

    # ›——————————————————  Cache / Broker  ——————————————————‹
    REDIS_URL: str = "redis://redis:6379/0"

    # ›——————————————————  E-mail  ——————————————————‹
    EMAIL_BACKEND: str = Field(
        default="console",
        description="console | ses | sendgrid",
    )
    SES_REGION: Optional[str] = None
    SENDGRID_API_KEY: Optional[str] = None
    EMAIL_FROM: str = "no-reply@scheduler.local"

    # ›——————————————————  Storage (S3)  ——————————————————‹
    S3_ENDPOINT_URL: Optional[str] = None  # e.g. http://minio:9000 for dev
    S3_BUCKET: str = "event-brand"
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None

    # ›——————————————————  External APIs  ——————————————————‹
    FX_API_URL: AnyHttpUrl = "https://api.exchangerate.host/latest"
    FX_REFRESH_HOURS: int = 24

    # ›——————————————————  Front-end  ——————————————————‹
    FRONTEND_URL: AnyHttpUrl = "http://localhost:5173"

    # ›——————————————————  Security  ——————————————————‹
    SECRET_KEY: str = Field(
        ...,
        min_length=32,
        description="Used for signing JWT, cookies, etc.",
    )

    # ›——————————————————  Misc  ——————————————————‹
    PROJECT_ROOT: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parents[2],
        description="Repo root path",
    )

    # ——— Derived / Validators ———————————————————————————

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors(cls, v: str | List[str]) -> List[AnyHttpUrl]:
        """
        Allows comma-separated string or JSON list.
        """
        if isinstance(v, str) and v.startswith("["):
            # Passed as JSON array
            return [url.strip().strip('"') for url in v.strip("[]").split(",")]
        if isinstance(v, str):
            # Comma-separated
            return [url.strip() for url in v.split(",")]
        return v

    @validator("DEBUG", pre=True)
    def set_debug_false_in_prod(cls, v, values):
        """
        Force DEBUG=False when APP_ENV == 'prod' unless explicitly set.
        """
        if values.get("APP_ENV") == "prod":
            return False
        return v

    # ——— Logging helper ————————————————————————————————

    def configure_logging(self) -> None:
        """
        Configure the root logger exactly once.
        """
        logging.basicConfig(
            format="%(levelprefix)s | %(asctime)s | %(name)s | %(message)s",
            level=getattr(logging, self.LOG_LEVEL.upper(), "INFO"),
        )
        logging.getLogger("sqlalchemy.engine").setLevel(
            logging.INFO if self.DEBUG else logging.WARNING
        )

    # ——— Pydantic config ———————————————————————————————

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


# Lazily-initialised singleton (ensures .env parsed only once)
@lru_cache
def _get_settings() -> Settings:  # noqa: D401  (fast, cached)
    s = Settings()
    s.configure_logging()
    return s


settings: Settings = _get_settings()
