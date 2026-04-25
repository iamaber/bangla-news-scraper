from datetime import date, datetime

from pydantic import BaseModel, Field

from bangla_news_scraper.models import JobInfo, JobStatus, SourceName


class JobCreateRequest(BaseModel):
    source: SourceName
    start_date: date
    end_date: date
    max_articles: int = Field(default=100, ge=1, le=500)


class JobResponse(BaseModel):
    job_id: str
    source: SourceName
    status: JobStatus
    start_date: date
    end_date: date
    max_articles: int
    csv_path: str
    row_count: int
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    error: str | None


class JobPathResponse(BaseModel):
    job_id: str
    status: JobStatus
    csv_path: str


class SourcesResponse(BaseModel):
    sources: tuple[SourceName, ...]


def build_job_response(job: JobInfo) -> JobResponse:
    return JobResponse(
        job_id=job.job_id,
        source=job.source,
        status=job.status,
        start_date=job.start_date,
        end_date=job.end_date,
        max_articles=job.max_articles,
        csv_path=str(job.csv_path),
        row_count=job.row_count,
        created_at=job.created_at,
        started_at=job.started_at,
        finished_at=job.finished_at,
        error=job.error,
    )
