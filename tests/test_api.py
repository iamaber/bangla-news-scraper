from fastapi.testclient import TestClient

from bangla_news_scraper.api.app import app


client = TestClient(app)


def test_health():
    response = client.get("/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_sources():
    response = client.get("/v1/sources")
    assert response.status_code == 200
    data = response.json()
    assert "sources" in data
    assert len(data["sources"]) == 4


def test_get_nonexistent_job():
    response = client.get("/v1/jobs/nonexistent-id")
    assert response.status_code == 404


def test_create_job_invalid_source():
    response = client.post(
        "/v1/jobs",
        json={
            "source": "fake-source",
            "start_date": "2024-01-01",
            "end_date": "2024-01-01",
        },
    )
    assert response.status_code == 422
