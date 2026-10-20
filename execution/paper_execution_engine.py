import os
from datetime import datetime, timezone

from execution.execution_result import ExecutionResult
from execution.paper_position_sizer import PaperPositionSizer


class PaperExecutionEngine:

    def __init__(self, position_sizer=None):
        self.position_sizer = position_sizer or PaperPositionSizer()

    @staticmethod
    def _calculate_sl_tp(action, price):
        """Calculate SL/TP from env percentages. Returns (sl, tp) or (None, None)."""
        if os.getenv("PHOENIX_AUTO_SL_TP", "0").strip() != "1":
            return None, None

        sl_pct = float(os.getenv("PHOENIX_SL_PERCENT", "1.0")) / 100.0
        tp_pct = float(os.getenv("PHOENIX_TP_PERCENT", "2.0")) / 100.0

        if action == "BUY":
            sl = price * (1 - sl_pct)
            tp = price * (1 + tp_pct)
        elif action == "SELL":
            sl = price * (1 + sl_pct)
            tp = price * (1 - tp_pct)
        else:
            return None, None

        return sl, tp

    def execute(
        self,
        action_proposal,
        price,
        symbol="BTCUSDT",
        quantity=None,
        balance=None,
        position_size_percent=None,
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
                reason=reason or "No execution required",
            )

        if status == "REJECTED":
            return ExecutionResult(
                status="NOT_EXECUTED",
                action=action,
                symbol=symbol,
                price=price,
                quantity=quantity,
                reason=reason or "Action proposal was rejected",
            )

        if action not in ("BUY", "SELL"):
            return ExecutionResult(
                status="NOT_EXECUTED",
                action=action,
                symbol=symbol,
                price=price,
                quantity=quantity,
                reason="Unsupported action",
            )

        if quantity is None:
            quantity = self.position_sizer.calculate_quantity(
                balance=balance,
                position_size_percent=position_size_percent,
                entry_price=price,
            )

        if quantity <= 0:
            return ExecutionResult(
                status="NOT_EXECUTED",
                action=action,
                symbol=symbol,
                price=price,
                quantity=quantity,
                reason="Invalid quantity",
            )

        sl, tp = self._calculate_sl_tp(action, price)

        return ExecutionResult(
            status="EXECUTED",
            action=action,
            symbol=symbol,
            price=price,
            quantity=quantity,
            reason=reason or "Paper execution completed",
            sl=sl,
            tp=tp,
        )