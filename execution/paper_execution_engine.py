from execution.execution_result import ExecutionResult
from execution.paper_position_sizer import PaperPositionSizer


class PaperExecutionEngine:

    def __init__(self, position_sizer=None):
        self.position_sizer = position_sizer or PaperPositionSizer()

    def execute(
        self,
        action_proposal,
        price,
        symbol="BTCUSDT",
        quantity=None,
        balance=None,
        position_size_percent=None
    ):
        action = getattr(action_proposal, "action", None)
        status = getattr(action_proposal, "status", None)
        reason = getattr(action_proposal, "reason", None)

        if action in (None, "WAIT"):
            return ExecutionResult(
                status="NOT_EXECUTED",
                action=action or "WAIT",
                symbol=symbol,
                price=price,
                quantity=quantity,
                reason=reason or "No execution required"
            )

        if status == "REJECTED":
            return ExecutionResult(
                status="NOT_EXECUTED",
                action=action,
                symbol=symbol,
                price=price,
                quantity=quantity,
                reason=reason or "Action proposal was rejected"
            )

        if action not in ("BUY", "SELL"):
            return ExecutionResult(
                status="NOT_EXECUTED",
                action=action,
                symbol=symbol,
                price=price,
                quantity=quantity,
                reason="Unsupported action"
            )

        if quantity is None:
            quantity = self.position_sizer.calculate_quantity(
                balance=balance,
                position_size_percent=position_size_percent,
                entry_price=price
            )

        if quantity <= 0:
            return ExecutionResult(
                status="NOT_EXECUTED",
                action=action,
                symbol=symbol,
                price=price,
                quantity=quantity,
                reason="Invalid quantity"
            )

        return ExecutionResult(
            status="EXECUTED",
            action=action,
            symbol=symbol,
            price=price,
            quantity=quantity,
            reason=reason or "Paper execution completed"
        )