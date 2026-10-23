"""
Live position tracker — reconstructs conceptual positions from fills.
Includes file persistence for crash-safe operation.
"""
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class LivePosition:
    # ─── Core ───
    symbol: str
    side: str
    entry_price: float
    quantity: float
    entry_order_id: str
    opened_at: datetime
    sl: Optional[float] = None
    tp: Optional[float] = None
    realized_pnl: float = 0.0
    fees: float = 0.0
    metadata: dict = field(default_factory=dict)

    # ─── Compat with PaperPosition ───
    leverage: float = 1.0
    initial_sl: Optional[float] = None
    partial_closed: bool = False
    be_moved: bool = False
    best_price_seen: Optional[float] = None
    realized_partial_pnl: float = 0.0
    decision: Optional[object] = None

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


def _pos_to_dict(p: LivePosition) -> dict:
    return {
        "symbol": p.symbol,
        "side": p.side,
        "entry_price": p.entry_price,
        "quantity": p.quantity,
        "entry_order_id": p.entry_order_id,
        "opened_at": p.opened_at.isoformat(),
        "sl": p.sl,
        "tp": p.tp,
        "realized_pnl": p.realized_pnl,
        "fees": p.fees,
        "metadata": p.metadata,
        "leverage": p.leverage,
        "initial_sl": p.initial_sl,
        "partial_closed": p.partial_closed,
        "be_moved": p.be_moved,
        "best_price_seen": p.best_price_seen,
        "realized_partial_pnl": p.realized_partial_pnl,
    }


def _pos_from_dict(d: dict) -> LivePosition:
    opened = d.get("opened_at")
    if isinstance(opened, str):
        try:
            opened = datetime.fromisoformat(opened)
        except ValueError:
            opened = datetime.now(timezone.utc)
    elif not isinstance(opened, datetime):
        opened = datetime.now(timezone.utc)

    return LivePosition(
        symbol=d["symbol"],
        side=d["side"],
        entry_price=float(d["entry_price"]),
        quantity=float(d["quantity"]),
        entry_order_id=d.get("entry_order_id", ""),
        opened_at=opened,
        sl=d.get("sl"),
        tp=d.get("tp"),
        realized_pnl=float(d.get("realized_pnl", 0.0)),
        fees=float(d.get("fees", 0.0)),
        metadata=d.get("metadata") or {},
        leverage=float(d.get("leverage", 1.0)),
        initial_sl=d.get("initial_sl"),
        partial_closed=bool(d.get("partial_closed", False)),
        be_moved=bool(d.get("be_moved", False)),
        best_price_seen=d.get("best_price_seen"),
        realized_partial_pnl=float(d.get("realized_partial_pnl", 0.0)),
    )


class LivePositionTracker:
    STATE_VERSION = 1

    def __init__(self):
        self.positions: Dict[str, LivePosition] = {}

    def get(self, symbol: str) -> Optional[LivePosition]:
        return self.positions.get(symbol)

    def has_position(self, symbol: str) -> bool:
        return symbol in self.positions

    def open_from_fill(
        self, symbol, side, execution_result,
        sl=None, tp=None, fee_pct=0.0006, metadata=None,
    ) -> Optional[LivePosition]:
        if not execution_result.success:
            logger.warning(f"open_from_fill: exec not success")
            return None
        if execution_result.filled_quantity <= 0:
            logger.warning("open_from_fill: zero filled qty")
            return None
        if symbol in self.positions:
            logger.warning(f"open_from_fill: position exists for {symbol}")
            return None

        entry = execution_result.avg_fill_price
        qty = execution_result.filled_quantity
        fees = entry * qty * fee_pct

        pos = LivePosition(
            symbol=symbol,
            side=side.upper(),
            entry_price=entry,
            quantity=qty,
            entry_order_id=execution_result.order_id,
            opened_at=datetime.now(timezone.utc),
            sl=sl, tp=tp, fees=fees,
            initial_sl=sl,
            metadata=metadata or {},
        )
        self.positions[symbol] = pos
        logger.info(f"Position opened: {symbol} {pos.side} {qty} @ {entry}")
        return pos

    def close_from_fill(
        self, symbol, execution_result, fee_pct=0.0006,
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

    # ─── Persistence ───
    def to_dict(self) -> dict:
        return {sym: _pos_to_dict(p) for sym, p in self.positions.items()}

    def from_dict(self, data: dict) -> None:
        self.positions = {}
        for sym, d in (data or {}).items():
            try:
                self.positions[sym] = _pos_from_dict(d)
            except Exception as e:
                logger.warning(f"skip malformed position {sym}: {e}")

    def save_to_file(self, path) -> bool:
        """Atomic write. Returns True on success."""
        path = Path(path)
        try:
            payload = {
                "version": self.STATE_VERSION,
                "saved_at": datetime.now(timezone.utc).isoformat(),
                "positions": self.to_dict(),
            }
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(path.suffix + ".tmp")
            tmp.write_text(
                json.dumps(payload, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            tmp.replace(path)
            return True
        except Exception as e:
            logger.error(f"save_to_file failed: {e}")
            return False

    def load_from_file(self, path) -> bool:
        """
        Load from disk. Returns True if loaded or file absent.
        Returns False only on hard errors (version mismatch, corrupt JSON).
        """
        path = Path(path)
        if not path.exists():
            logger.info(f"no state file at {path}")
            return True

        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            logger.error(f"state file corrupted: {e}")
            backup = path.with_suffix(path.suffix + ".corrupt")
            try:
                path.replace(backup)
                logger.error(f"moved corrupted state to {backup}")
            except Exception:
                pass
            return False

        version = raw.get("version")
        if version != self.STATE_VERSION:
            backup = path.with_suffix(f".v{version}.bak")
            try:
                path.replace(backup)
                logger.warning(f"version {version} mismatch, backed up to {backup}")
            except Exception:
                pass
            return False

        self.from_dict(raw.get("positions", {}))
        logger.info(f"loaded {len(self.positions)} position(s) from {path}")
        return True