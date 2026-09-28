from execution.xt_futures_order_confirmation import (
    XTFuturesOrderConfirmation,
    XTFuturesOrderConfirmationState,
)


class XTFuturesOrderConfirmationInterpreter:
    FILLED = "FILLED"
    REJECTED_STATES = {"CANCELED", "REJECTED", "EXPIRED"}

    @staticmethod
    def _optional_float(value):
        if value is None:
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None

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

        executed_quantity = self._optional_float(
            result.get("executedQty")
        )
        average_price = self._optional_float(
            result.get("avgPrice")
        )

        if state == self.FILLED:
            return XTFuturesOrderConfirmation(
                state=XTFuturesOrderConfirmationState.CONFIRMED,
                order_id=str(order_id),
                executed_quantity=executed_quantity,
                average_price=average_price,
            )

        if state in self.REJECTED_STATES:
            return XTFuturesOrderConfirmation(
                state=XTFuturesOrderConfirmationState.REJECTED,
                order_id=str(order_id),
                error=f"Order state: {state}",
                executed_quantity=executed_quantity,
                average_price=average_price,
            )

        return XTFuturesOrderConfirmation(
            state=XTFuturesOrderConfirmationState.UNKNOWN,
            order_id=str(order_id),
            error=f"Order state: {state}",
            executed_quantity=executed_quantity,
            average_price=average_price,
        )
