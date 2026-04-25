import argparse
from datetime import date

from bangla_news_scraper.config import settings
from bangla_news_scraper.models import SOURCE_NAMES, ScrapeJobRequest
from bangla_news_scraper.services.jobs import job_service


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Bangla news scraping job")
    parser.add_argument("source", help="One of: bangladesh-pratidin, prothomalo, jugantor, samakal")
    parser.add_argument("start_date", help="Start date (YYYY-MM-DD)")
    parser.add_argument("end_date", help="End date (YYYY-MM-DD)")
    parser.add_argument("--max-articles", type=int, default=100, help="Maximum articles to scrape")
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    if args.source not in SOURCE_NAMES:
        parser.error(f"Invalid source '{args.source}'. Choose from: {', '.join(SOURCE_NAMES)}")
    request = ScrapeJobRequest(
        source=args.source,
        start_date=date.fromisoformat(args.start_date),
        end_date=date.fromisoformat(args.end_date),
        max_articles=args.max_articles,
        output_directory=settings.default_output_directory,
    )
    job = job_service.start_job(request)
    final_job = job_service.run_job(job.job_id)
    print(f"job_id={final_job.job_id}")
    print(f"status={final_job.status}")
    print(f"csv_path={final_job.csv_path}")
    print(f"rows={final_job.row_count}")
    if final_job.error:
        print(f"error={final_job.error}")
