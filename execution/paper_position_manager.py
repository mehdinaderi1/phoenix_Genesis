import os
from datetime import datetime, timezone

from execution.paper_position import PaperPosition, _fee_rate
from config.settings import Settings


class PaperPositionManager:

    def __init__(self):
        self.position = None

    def _auto_tp_sl(self, entry_price, side):
        tp_pct = getattr(Settings, "TP_PCT", 0.0020)
        sl_pct = getattr(Settings, "SL_PCT", 0.0010)
        if side == "BUY":
            return entry_price * (1 - sl_pct), entry_price * (1 + tp_pct)
        return entry_price * (1 + sl_pct), entry_price * (1 - tp_pct)

    def open_position(self, execution_result, decision=None):
        if self.position is not None:
            return None
        if execution_result.status != "EXECUTED":
            return None
        if execution_result.action not in ("BUY", "SELL"):
            return None
        if (
            not execution_result.symbol
            or execution_result.quantity is None
            or execution_result.quantity <= 0
            or execution_result.price is None
            or execution_result.price <= 0
        ):
            return None

        sl = getattr(execution_result, "sl", None)
        tp = getattr(execution_result, "tp", None)
        if getattr(Settings, "AUTO_TP_SL", True) and (sl is None or tp is None):
            auto_sl, auto_tp = self._auto_tp_sl(
                execution_result.price, execution_result.action
            )
            sl = sl if sl is not None else auto_sl
            tp = tp if tp is not None else auto_tp

        opened_at = None
        if (os.getenv("PHOENIX_AUTO_SL_TP", "0").strip() == "1"
                or getattr(Settings, "AUTO_TP_SL", False)):
            opened_at = datetime.now(timezone.utc).isoformat()

        self.position = PaperPosition(
            symbol=execution_result.symbol,
            side=execution_result.action,
            entry_price=execution_result.price,
            quantity=execution_result.quantity,
            decision=decision,
            sl=sl,
            tp=tp,
            opened_at=opened_at,
            leverage=float(getattr(Settings, "LEVERAGE", 1.0)),
        )
        return self.position

    def get_position(self):
        return self.position

    def calculate_pnl(self, current_price):
        if self.position is None:
            return 0.0
        return self.position.total_pnl(current_price)

    def close_position(self):
        position = self.position
        self.position = None
        return position

    # ─── PARTIAL ───
    def partial_close(self, current_price, fraction=0.5):
        if self.position is None:
            return None
        position = self.position
        if position.quantity <= 0:
            return None
        close_qty = position.quantity * fraction
        if close_qty <= 0:
            return None

        if position.side == "BUY":
            gross = (current_price - position.entry_price) * close_qty
        else:
            gross = (position.entry_price - current_price) * close_qty

        rate = _fee_rate()
        entry_fee = position.entry_price * close_qty * rate
        exit_fee = current_price * close_qty * rate
        net_pnl = gross - entry_fee - exit_fee

        position.quantity -= close_qty
        position.partial_closed = True
        position.realized_partial_pnl += net_pnl

        return {
            "closed_quantity": close_qty,
            "exit_price": current_price,
            "partial_pnl": net_pnl,
            "remaining_quantity": position.quantity,
        }

    # ─── SL MOVE (BE / trailing) ───
    def move_sl(self, new_sl):
        if self.position is None:
            return False
        old_sl = self.position.sl
        self.position.sl = new_sl
        if abs(new_sl - self.position.entry_price) < 1e-9:
            self.position.be_moved = True
        return True

    def close_position_with_pnl(self, current_price, exit_reason=None):
        if self.position is None:
            return None

        position = self.position
        gross_pnl = position.unrealized_pnl(current_price)
        fees = position.fee_breakdown(current_price)
        realized_pnl = gross_pnl - fees["total"]
        self.position = None

        return {
            "position": position,
            "exit_price": current_price,
            "exit_reason": exit_reason,
            "gross_pnl": gross_pnl,
            "fees": fees,
            "realized_pnl": realized_pnl,
        }