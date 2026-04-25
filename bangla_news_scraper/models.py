from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Literal

SourceName = Literal["bangladesh-pratidin", "prothomalo", "jugantor", "samakal"]
SOURCE_NAMES: tuple[SourceName, ...] = (
    "bangladesh-pratidin",
    "prothomalo",
    "jugantor",
    "samakal",
)


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass(slots=True)
class ScrapeConfig:
    start_date: date
    end_date: date
    max_articles: int = 100
    request_timeout_seconds: float = 20.0
    user_agent: str = (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )

    def __post_init__(self) -> None:
        if self.end_date < self.start_date:
            raise ValueError("end_date must not be earlier than start_date")
        if self.max_articles < 1:
            raise ValueError("max_articles must be at least 1")
        if self.request_timeout_seconds <= 0:
            raise ValueError("request_timeout_seconds must be greater than 0")


@dataclass(slots=True)
class ArticleRecord:
    source: SourceName
    url: str
    date_published: str
    headline: str
    article_body: str
    writer: str = "Unknown"


@dataclass(slots=True)
class ScrapeJobRequest:
    source: SourceName
    start_date: date
    end_date: date
    max_articles: int = 100
    output_directory: Path | None = None

    def __post_init__(self) -> None:
        if self.end_date < self.start_date:
            raise ValueError("end_date must not be earlier than start_date")
        if self.max_articles < 1:
            raise ValueError("max_articles must be at least 1")


@dataclass(slots=True)
class JobInfo:
    job_id: str
    source: SourceName
    status: JobStatus
    start_date: date
    end_date: date
    max_articles: int
    output_directory: Path
    csv_path: Path
    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None
    row_count: int = 0
    error: str | None = None
    error_code: str | None = None
