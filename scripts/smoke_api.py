import time
from datetime import date

from fastapi.testclient import TestClient

from bangla_news_scraper.api.app import app


def _wait_for_job(client: TestClient, job_id: str, timeout_seconds: float = 60.0) -> dict:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        response = client.get(f"/v1/jobs/{job_id}")
        response.raise_for_status()
        payload = response.json()
        if payload["status"] in {"succeeded", "failed"}:
            return payload
        time.sleep(0.5)
    raise TimeoutError(f"Job {job_id} did not finish within {timeout_seconds}s")


def main() -> int:
    client = TestClient(app)

    health = client.get("/v1/health")
    if health.status_code != 200:
        print(f"[api-smoke] health failed: {health.status_code}")
        return 1

    sources = client.get("/v1/sources")
    if sources.status_code != 200:
        print(f"[api-smoke] sources failed: {sources.status_code}")
        return 1

    create = client.post(
        "/v1/jobs",
        json={
            "source": "prothomalo",
            "start_date": date(2024, 1, 2).isoformat(),
            "end_date": date(2024, 1, 2).isoformat(),
            "max_articles": 2,
        },
    )
    if create.status_code != 202:
        print(f"[api-smoke] create failed: {create.status_code} {create.text}")
        return 1

    job_id = create.json()["job_id"]
    result = _wait_for_job(client, job_id)
    if result["status"] != "succeeded":
        print(f"[api-smoke] job failed: {result}")
        return 1

    path_resp = client.get(f"/v1/jobs/{job_id}/csv-path")
    if path_resp.status_code != 200:
        print(f"[api-smoke] csv-path failed: {path_resp.status_code}")
        return 1

    dl_resp = client.get(f"/v1/jobs/{job_id}/download")
    if dl_resp.status_code != 200:
        print(f"[api-smoke] download failed: {dl_resp.status_code}")
        return 1
    if "Date Published" not in dl_resp.text:
        print("[api-smoke] download content missing expected CSV header")
        return 1

    print(f"[api-smoke] success job_id={job_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
