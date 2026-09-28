from execution.xt_futures_attempt_result import (
    XTFuturesAttemptResult,
)
from execution.xt_futures_attempt_state import (
    XTFuturesAttemptState,
)
from execution.xt_futures_order_confirmation import (
    XTFuturesOrderConfirmationState,
)


class XTFuturesConfirmationStateResolver:
    """
    Maps order confirmation state to the Phoenix attempt state.

    This resolver does not perform network requests and does not
    interpret exchange responses.
    """

    def resolve(
        self,
        idempotency_key,
        confirmation,
    ):
        if not idempotency_key:
            raise ValueError(
                "idempotency_key is required"
            )

        if confirmation is None:
            raise ValueError(
                "confirmation is required"
            )

        state = confirmation.state

        if state == XTFuturesOrderConfirmationState.CONFIRMED:
            return XTFuturesAttemptResult(
                state=XTFuturesAttemptState.CONFIRMED,
                idempotency_key=idempotency_key,
            )

        if state == XTFuturesOrderConfirmationState.REJECTED:
            return XTFuturesAttemptResult(
                state=XTFuturesAttemptState.REJECTED,
                idempotency_key=idempotency_key,
                error=confirmation.error or "Order rejected",
            )

        if state == XTFuturesOrderConfirmationState.UNKNOWN:
            return XTFuturesAttemptResult(
                state=XTFuturesAttemptState.UNKNOWN,
                idempotency_key=idempotency_key,
                error=confirmation.error or "Order state unknown",
            )

        raise TypeError(
            "unsupported confirmation state"
        )
