from dataclasses import dataclass

from execution.xt_futures_attempt_state import XTFuturesAttemptState


@dataclass(frozen=True)
class XTFuturesAttemptResult:
    """State of one logical execution attempt."""

    state: XTFuturesAttemptState
    idempotency_key: str
    error: str | None = None

    def __post_init__(self):
        if not self.idempotency_key:
            raise ValueError(
                "idempotency_key is required"
            )

        if self.state == XTFuturesAttemptState.REJECTED:
            if not self.error:
                raise ValueError(
                    "REJECTED attempt requires error"
                )
