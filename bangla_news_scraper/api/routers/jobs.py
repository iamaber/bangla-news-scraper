from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse

from bangla_news_scraper.api.schemas import (
    JobCreateRequest,
    JobPathResponse,
    JobResponse,
    build_job_response,
)
from bangla_news_scraper.errors import JobNotFoundError
from bangla_news_scraper.models import ScrapeJobRequest
from bangla_news_scraper.services.jobs import job_service

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobResponse, status_code=202)
def create_job(payload: JobCreateRequest, background_tasks: BackgroundTasks) -> JobResponse:
    request = ScrapeJobRequest(
        source=payload.source,
        start_date=payload.start_date,
        end_date=payload.end_date,
        max_articles=payload.max_articles,
    )
    job = job_service.start_job(request)
    background_tasks.add_task(job_service.run_job, job.job_id)
    return build_job_response(job)


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str) -> JobResponse:
    try:
        job = job_service.get_job(job_id)
    except JobNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return build_job_response(job)


@router.get("/{job_id}/csv-path", response_model=JobPathResponse)
def get_job_csv_path(job_id: str) -> JobPathResponse:
    try:
        job = job_service.get_job(job_id)
    except JobNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return JobPathResponse(job_id=job.job_id, status=job.status, csv_path=str(job.csv_path))


@router.get("/{job_id}/download")
def download_csv(job_id: str) -> FileResponse:
    try:
        job = job_service.get_job(job_id)
    except JobNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    csv_path = Path(job.csv_path)
    if not csv_path.exists():
        raise HTTPException(status_code=404, detail="CSV artifact not ready")
    return FileResponse(path=csv_path, media_type="text/csv", filename=csv_path.name)
