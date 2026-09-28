from execution.xt_futures_order_confirmation import (
    XTFuturesOrderConfirmation,
    XTFuturesOrderConfirmationState,
)


class XTFuturesOrderConfirmationInterpreter:
    """
    Interprets a normalized XT Futures order-detail response.

    Only a verified FILLED state is treated as CONFIRMED.
    """

    FILLED = "FILLED"

    REJECTED_STATES = {
        "CANCELED",
        "REJECTED",
        "EXPIRED",
    }

    def interpret(self, response):
        if response is None:
            raise TypeError("response is required")

        if not getattr(response, "ok", False):
            return XTFuturesOrderConfirmation(
                state=XTFuturesOrderConfirmationState.UNKNOWN,
                error=response.error or "HTTP request failed",
            )

        body = getattr(response, "body", None)

        if not isinstance(body, dict):
            return XTFuturesOrderConfirmation(
                state=XTFuturesOrderConfirmationState.UNKNOWN,
                error="Invalid order response body",
            )

        result = body.get("result")

        if not isinstance(result, dict):
            return XTFuturesOrderConfirmation(
                state=XTFuturesOrderConfirmationState.UNKNOWN,
                error="Order result is unavailable",
            )

        order_id = result.get("orderId")
        state = result.get("state")

        if not order_id or not state:
            return XTFuturesOrderConfirmation(
                state=XTFuturesOrderConfirmationState.UNKNOWN,
                error="Order confirmation data is incomplete",
            )

        if state == self.FILLED:
            return XTFuturesOrderConfirmation(
                state=XTFuturesOrderConfirmationState.CONFIRMED,
                order_id=str(order_id),
            )

        if state in self.REJECTED_STATES:
            return XTFuturesOrderConfirmation(
                state=XTFuturesOrderConfirmationState.REJECTED,
                order_id=str(order_id),
                error=f"Order state: {state}",
            )

        return XTFuturesOrderConfirmation(
            state=XTFuturesOrderConfirmationState.UNKNOWN,
            order_id=str(order_id),
            error=f"Order state: {state}",
        )
