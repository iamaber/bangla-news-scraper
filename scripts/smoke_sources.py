from datetime import date

from bangla_news_scraper.models import JobStatus, ScrapeJobRequest
from bangla_news_scraper.services.jobs import job_service

SMOKE_CASES = [
    ("prothomalo", date(2024, 1, 2), date(2024, 1, 2)),
    ("samakal", date(2024, 9, 5), date(2024, 9, 5)),
    ("bangladesh-pratidin", date(2025, 11, 6), date(2025, 11, 6)),
    ("jugantor", date(2024, 8, 12), date(2024, 8, 12)),
]


def main() -> int:
    failures = 0
    for source, start_date, end_date in SMOKE_CASES:
        print(f"[smoke] source={source} start={start_date} end={end_date}")
        job = job_service.start_job(
            ScrapeJobRequest(
                source=source,
                start_date=start_date,
                end_date=end_date,
                max_articles=3,
            )
        )
        result = job_service.run_job(job.job_id)
        exists = result.csv_path.exists()
        print(
            f"[smoke] status={result.status} rows={result.row_count} "
            f"csv={result.csv_path} exists={exists}"
        )
        if result.error:
            print(f"[smoke] error={result.error}")
        if result.status is not JobStatus.SUCCEEDED or result.row_count < 1 or not exists:
            failures += 1

    if failures:
        print(f"[smoke] failed_cases={failures}")
        return 1

    print("[smoke] all source checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
