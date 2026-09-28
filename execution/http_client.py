from dataclasses import dataclass


@dataclass(frozen=True)
class HttpResponse:
    """Minimal HTTP response contract."""

    status_code: int
    body: str


class HttpClient:
    """Minimal HTTP client contract used by transports."""

    def post(
        self,
        endpoint,
        headers,
        body,
        timeout=10
    ):
        raise NotImplementedError
