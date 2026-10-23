"""
Live position tracker — reconstructs conceptual positions from fills.
Unlike paper positions, these come from real XT fills.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


@dataclass
class LivePosition:
    symbol: str
    side: str              # BUY or SELL
    entry_price: float
    quantity: float
    entry_order_id: str
    opened_at: datetime
    sl: Optional[float] = None
    tp: Optional[float] = None
    realized_pnl: float = 0.0
    fees: float = 0.0
    metadata: dict = field(default_factory=dict)

    def unrealized_pnl(self, current_price: float) -> float:
        if self.side == "BUY":
            gross = (current_price - self.entry_price) * self.quantity
        else:
            gross = (self.entry_price - current_price) * self.quantity
        return gross - self.fees

    def unrealized_pnl_pct(self, current_price: float) -> float:
        if self.entry_price <= 0:
            return 0.0
        if self.side == "BUY":
            return (current_price - self.entry_price) / self.entry_price * 100
        return (self.entry_price - current_price) / self.entry_price * 100


class LivePositionTracker:
    """
    Tracks one live position per symbol (single-position mode).
    Fed by OrderExecutor.ExecutionResult.
    """
    def __init__(self):
        self.positions: Dict[str, LivePosition] = {}

    def get(self, symbol: str) -> Optional[LivePosition]:
        return self.positions.get(symbol)

    def has_position(self, symbol: str) -> bool:
        return symbol in self.positions

    def open_from_fill(
        self,
        symbol: str,
        side: str,
        execution_result,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        fee_pct: float = 0.0006,
        metadata: Optional[dict] = None,
    ) -> Optional[LivePosition]:
        if not execution_result.success:
            logger.warning(f"open_from_fill: exec not success ({execution_result.status})")
            return None
        if execution_result.filled_quantity <= 0:
            logger.warning("open_from_fill: zero filled qty")
            return None
        if symbol in self.positions:
            logger.warning(f"open_from_fill: position already exists for {symbol}")
            return None

        entry = execution_result.avg_fill_price
        qty = execution_result.filled_quantity
        cost = entry * qty
        fees = cost * fee_pct

        pos = LivePosition(
            symbol=symbol,
            side=side.upper(),
            entry_price=entry,
            quantity=qty,
            entry_order_id=execution_result.order_id,
            opened_at=datetime.now(timezone.utc),
            sl=sl, tp=tp,
            fees=fees,
            metadata=metadata or {},
        )
        self.positions[symbol] = pos
        logger.info(f"Position opened: {symbol} {pos.side} {qty} @ {entry} "
                    f"sl={sl} tp={tp} fees={fees:.6f}")
        return pos

    def close_from_fill(
        self,
        symbol: str,
        execution_result,
        fee_pct: float = 0.0006,
    ) -> Optional[dict]:
        pos = self.positions.get(symbol)
        if pos is None:
            logger.warning(f"close_from_fill: no position for {symbol}")
            return None
        if not execution_result.success:
            logger.warning(f"close_from_fill: exec not success")
            return None

        exit_price = execution_result.avg_fill_price
        exit_qty = min(execution_result.filled_quantity, pos.quantity)

        if pos.side == "BUY":
            gross = (exit_price - pos.entry_price) * exit_qty
        else:
            gross = (pos.entry_price - exit_price) * exit_qty

        exit_fees = exit_price * exit_qty * fee_pct
        net = gross - pos.fees - exit_fees

        result = {
            "symbol": symbol,
            "side": pos.side,
            "entry_price": pos.entry_price,
            "exit_price": exit_price,
            "quantity": exit_qty,
            "gross_pnl": gross,
            "total_fees": pos.fees + exit_fees,
            "realized_pnl": net,
            "entry_order_id": pos.entry_order_id,
            "exit_order_id": execution_result.order_id,
        }

        if exit_qty >= pos.quantity * 0.999:
            del self.positions[symbol]
            logger.info(f"Position closed: {symbol} net={net:+.6f}")
        else:
            pos.quantity -= exit_qty
            logger.info(f"Position partially closed: {symbol} remaining={pos.quantity}")

        return result

    def to_dict(self) -> dict:
        return {
            sym: {
                "side": p.side, "entry_price": p.entry_price,
                "quantity": p.quantity, "sl": p.sl, "tp": p.tp,
                "opened_at": p.opened_at.isoformat(),
                "fees": p.fees, "realized_pnl": p.realized_pnl,
            }
            for sym, p in self.positions.items()
        }

    def from_dict(self, data: dict):
        self.positions = {}
        for sym, d in data.items():
            self.positions[sym] = LivePosition(
                symbol=sym, side=d["side"],
                entry_price=d["entry_price"], quantity=d["quantity"],
                entry_order_id="", opened_at=datetime.fromisoformat(d["opened_at"]),
                sl=d.get("sl"), tp=d.get("tp"),
                fees=d.get("fees", 0.0), realized_pnl=d.get("realized_pnl", 0.0),
            )