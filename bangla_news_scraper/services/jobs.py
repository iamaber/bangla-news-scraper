import threading
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from bangla_news_scraper.config import settings
from bangla_news_scraper.errors import JobNotFoundError, JobQueueFullError
from bangla_news_scraper.models import JobInfo, JobStatus, ScrapeConfig, ScrapeJobRequest
from bangla_news_scraper.services.csv_writer import write_articles_to_csv
from bangla_news_scraper.sources.registry import create_scraper


MAX_COMPLETED_JOBS = 1000


class JobService:
    def __init__(self) -> None:
        self._jobs: dict[str, JobInfo] = {}
        self._lock = threading.Lock()

    def _evict_old_jobs(self) -> None:
        finished = [
            (jid, j)
            for jid, j in self._jobs.items()
            if j.status in (JobStatus.SUCCEEDED, JobStatus.FAILED)
        ]
        if len(finished) <= MAX_COMPLETED_JOBS:
            return
        finished.sort(key=lambda pair: pair[1].finished_at or datetime.min.replace(tzinfo=UTC))
        for jid, _ in finished[: len(finished) - MAX_COMPLETED_JOBS]:
            del self._jobs[jid]

    def _current_counts(self) -> tuple[int, int]:
        running = 0
        queued = 0
        for job in self._jobs.values():
            if job.status == JobStatus.RUNNING:
                running += 1
            elif job.status == JobStatus.QUEUED:
                queued += 1
        return running, queued

    def start_job(self, request: ScrapeJobRequest) -> JobInfo:
        created_at = datetime.now(UTC)
        job_id = uuid4().hex
        output_directory = request.output_directory or settings.default_output_directory
        csv_path = Path(output_directory) / request.source / f"{job_id}.csv"
        job = JobInfo(
            job_id=job_id,
            source=request.source,
            status=JobStatus.QUEUED,
            start_date=request.start_date,
            end_date=request.end_date,
            max_articles=request.max_articles,
            output_directory=Path(output_directory),
            csv_path=csv_path,
            created_at=created_at,
        )
        with self._lock:
            running, queued = self._current_counts()
            if running >= settings.max_running_jobs and queued >= settings.max_queued_jobs:
                raise JobQueueFullError("Job queue is full")
            self._jobs[job_id] = job
        return job

    def get_job(self, job_id: str) -> JobInfo:
        with self._lock:
            job = self._jobs.get(job_id)
        if job is None:
            raise JobNotFoundError(f"No job found for id: {job_id}")
        return job

    def list_jobs(self) -> list[JobInfo]:
        with self._lock:
            return list(self._jobs.values())

    def run_job(self, job_id: str) -> JobInfo:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                raise JobNotFoundError(f"No job found for id: {job_id}")
            if job.status not in (JobStatus.QUEUED, JobStatus.FAILED):
                raise ValueError(f"Job {job_id} is already {job.status.value}")
            job.status = JobStatus.RUNNING
            job.started_at = datetime.now(UTC)
            job.error = None

        try:
            scraper = create_scraper(job.source)
            config = ScrapeConfig(
                start_date=job.start_date,
                end_date=job.end_date,
                max_articles=job.max_articles,
                request_timeout_seconds=settings.request_timeout_seconds,
                user_agent=settings.user_agent,
            )
            articles = scraper.scrape(config)
            rows = write_articles_to_csv(job.csv_path, articles)
            with self._lock:
                job.row_count = rows
                job.status = JobStatus.SUCCEEDED
                job.finished_at = datetime.now(UTC)
                job.error = None
                job.error_code = None
                self._evict_old_jobs()
        except Exception:
            with self._lock:
                job.status = JobStatus.FAILED
                job.error = "Scrape job failed"
                job.error_code = "SCRAPE_FAILED"
                job.finished_at = datetime.now(UTC)
                self._evict_old_jobs()

        return job


job_service = JobService()
