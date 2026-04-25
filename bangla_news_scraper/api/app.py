from fastapi import FastAPI

from bangla_news_scraper.api.routers.health import router as health_router
from bangla_news_scraper.api.routers.jobs import router as jobs_router
from bangla_news_scraper.api.routers.sources import router as sources_router


def create_app() -> FastAPI:
    app = FastAPI(title="Bangla News Scraper API", version="0.1.0")
    app.include_router(health_router, prefix="/v1")
    app.include_router(sources_router, prefix="/v1")
    app.include_router(jobs_router, prefix="/v1")
    return app


app = create_app()
