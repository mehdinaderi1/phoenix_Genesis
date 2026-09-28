from dataclasses import dataclass


@dataclass(frozen=True)
class XTFuturesResponse:
    """Normalized XT Futures HTTP response."""

    status_code: int
    ok: bool
    body: dict | None
    raw_body: str
    error: str | None = None
