from execution.execution_result import ExecutionResult
from execution.xt_futures_order_confirmation import (
    XTFuturesOrderConfirmation,
    XTFuturesOrderConfirmationState,
)


class XTFuturesExecutionResultBridge:
    def build(
        self,
        confirmation,
        action,
        symbol,
    ):
        if not isinstance(
            confirmation,
            XTFuturesOrderConfirmation,
        ):
            raise TypeError(
                "confirmation must be XTFuturesOrderConfirmation"
            )

        if action not in ("BUY", "SELL"):
            raise ValueError("action must be BUY or SELL")

        if not symbol:
            raise ValueError("symbol is required")

        if confirmation.state != XTFuturesOrderConfirmationState.CONFIRMED:
            return None

        if (
            confirmation.executed_quantity is None
            or confirmation.executed_quantity <= 0
        ):
            return None

        if (
            confirmation.average_price is None
            or confirmation.average_price <= 0
        ):
            return None

        return ExecutionResult(
            status="EXECUTED",
            action=action,
            symbol=symbol,
            price=confirmation.average_price,
            quantity=confirmation.executed_quantity,
        )
