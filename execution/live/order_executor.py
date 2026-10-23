"""
High-level order executor — place + confirm.
"""
from dataclasses import dataclass
from typing import Optional

from execution.live.order_state_machine import OrderStatus, OrderSnapshot
from execution.live.fill_confirmation import FillConfirmation


@dataclass
class ExecutionResult:
    success: bool
    order_id: Optional[str]
    status: OrderStatus
    filled_quantity: float
    avg_fill_price: float
    total_cost: float
    raw_snapshot: Optional[OrderSnapshot] = None
    error: Optional[str] = None
    timed_out: bool = False       # ← NEW

    @property
    def is_filled(self) -> bool:
        return self.status == OrderStatus.FILLED

    @property
    def is_partial(self) -> bool:
        return self.status == OrderStatus.PARTIALLY_FILLED

    def __repr__(self):
        if self.success:
            return (f"<Exec OK order={self.order_id} "
                    f"qty={self.filled_quantity:.8f} @ {self.avg_fill_price:.2f}>")
        return (f"<Exec FAIL order={self.order_id} "
                f"status={self.status.value} err={self.error}>")


class OrderExecutor:
    def __init__(self, exchange, default_timeout=30.0,
                 poll_interval=2.0, logger=None):
        self.exchange = exchange
        self.default_timeout = default_timeout
        self.poll_interval = poll_interval
        self.logger = logger or (lambda msg: None)

    def execute_limit(self, symbol, side, price, quantity,
                      timeout=None) -> ExecutionResult:
        timeout = timeout or self.default_timeout
        try:
            order_id = self.exchange.place_order(
                symbol=symbol, side=side, price=price,
                quantity=quantity, order_type="LIMIT",
            )
            self.logger(f"[Exec] placed {order_id}")
        except Exception as e:
            return ExecutionResult(
                success=False, order_id=None, status=OrderStatus.REJECTED,
                filled_quantity=0, avg_fill_price=0, total_cost=0,
                error=f"place failed: {e}",
            )

        confirmer = FillConfirmation(
            exchange=self.exchange,
            poll_interval=self.poll_interval,
            timeout=timeout,
            logger=self.logger,
        )
        snap = confirmer.wait_for_fill(order_id)

        if snap is None:
            return ExecutionResult(
                success=False, order_id=order_id, status=OrderStatus.UNKNOWN,
                filled_quantity=0, avg_fill_price=0, total_cost=0,
                error="no status ever observed",
            )

        return ExecutionResult(
            success=snap.status.is_successful,
            order_id=order_id, status=snap.status,
            filled_quantity=snap.filled_quantity,
            avg_fill_price=snap.avg_fill_price,
            total_cost=snap.filled_notional,
            raw_snapshot=snap,
            timed_out=(not snap.status.is_terminal),
            error="timed out while open" if not snap.status.is_terminal else None,
        )

    def cancel(self, order_id: str) -> bool:
        try:
            return self.exchange.cancel_order([order_id])
        except Exception as e:
            self.logger(f"[Exec] cancel failed: {e}")
            return False