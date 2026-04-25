from fastapi import APIRouter

from bangla_news_scraper.api.schemas import SourcesResponse
from bangla_news_scraper.sources.registry import available_sources

router = APIRouter(tags=["sources"])


@router.get("/sources", response_model=SourcesResponse)
def list_sources() -> SourcesResponse:
    return SourcesResponse(sources=available_sources())
