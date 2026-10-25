from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    cors_origins: str = "http://localhost:5173,http://localhost:8080"
    decision_cutoff_local_time: str = "11:00"
    decision_timezone: str = "Europe/London"
    database_path: str = "data/wind_jan2026.db"
    elexon_base_url: str = "https://data.elexon.co.uk/bmrs/api/v1"
    scope_start: str = "2026-01-01"
    scope_end: str = "2026-01-31"
    forecast_publish_from: str = "2025-12-01"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def db_path(self) -> Path:
        path = Path(self.database_path)
        if not path.is_absolute():
            path = BACKEND_ROOT / path
        return path


@lru_cache
def get_settings() -> Settings:
    return Settings()
