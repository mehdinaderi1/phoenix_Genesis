from dataclasses import dataclass
from enum import Enum


class XTFuturesOrderConfirmationState(str, Enum):
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class XTFuturesOrderConfirmation:
    state: XTFuturesOrderConfirmationState
    order_id: str | None = None
    error: str | None = None

    def __post_init__(self):
        if (
            self.state == XTFuturesOrderConfirmationState.CONFIRMED
            and not self.order_id
        ):
            raise ValueError(
                "CONFIRMED order requires order_id"
            )

        if (
            self.state == XTFuturesOrderConfirmationState.REJECTED
            and not self.error
        ):
            raise ValueError(
                "REJECTED order requires error"
            )
