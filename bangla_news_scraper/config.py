from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    default_output_directory: Path = Path("artifacts/csv")
    request_timeout_seconds: float = 20.0
    max_articles_limit: int = 500
    max_running_jobs: int = 2
    max_queued_jobs: int = 100
    job_start_wait_seconds: float = 5.0
    max_requests_per_minute_per_ip: int = 300
    api_key: str = "change-me"
    user_agent: str = (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )

    model_config = SettingsConfigDict(env_prefix="BNS_", env_file=".env", extra="ignore")


settings = AppSettings()
