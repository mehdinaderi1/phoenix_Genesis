from execution.xt_futures_attempt_result import XTFuturesAttemptResult
from execution.xt_futures_attempt_state import XTFuturesAttemptState
from execution.xt_futures_order_confirmation import (
    XTFuturesOrderConfirmationState,
)


class XTFuturesReconciler:
    """
    Converts an already-interpreted XT order confirmation
    into the Phoenix execution attempt state.

    This class does not:
    - create orders
    - retry orders
    - perform HTTP requests
    - mutate positions
    """

    def reconcile(self, idempotency_key, confirmation):
        if not idempotency_key:
            raise ValueError("idempotency_key is required")

        if confirmation is None:
            raise ValueError("confirmation is required")

        if confirmation.state == XTFuturesOrderConfirmationState.CONFIRMED:
            return XTFuturesAttemptResult(
                state=XTFuturesAttemptState.CONFIRMED,
                idempotency_key=idempotency_key,
            )

        if confirmation.state == XTFuturesOrderConfirmationState.REJECTED:
            return XTFuturesAttemptResult(
                state=XTFuturesAttemptState.REJECTED,
                idempotency_key=idempotency_key,
                error=confirmation.error or "Order rejected",
            )

        if confirmation.state == XTFuturesOrderConfirmationState.UNKNOWN:
            return XTFuturesAttemptResult(
                state=XTFuturesAttemptState.UNKNOWN,
                idempotency_key=idempotency_key,
                error=confirmation.error or "Order state unknown",
            )

        raise TypeError("unsupported confirmation state")
