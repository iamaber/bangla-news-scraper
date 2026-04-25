from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def build_session() -> Session:
    retry = Retry(
        total=3,
        connect=3,
        read=3,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session
