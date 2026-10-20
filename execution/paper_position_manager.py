import os
from datetime import datetime, timezone

from execution.paper_position import PaperPosition
from config.settings import Settings


class PaperPositionManager:

    def __init__(self):
        self.position = None

    def _auto_tp_sl(self, entry_price, side):
        """محاسبهٔ TP/SL از روی Settings"""
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
            leverage=float(getattr(Settings, "LEVERAGE", 1.0)),   # ← اضافه
        )

        return self.position

    def get_position(self):
        return self.position

    def calculate_pnl(self, current_price):
        if self.position is None:
            return 0.0
        return self.position.unrealized_pnl(current_price)

    def close_position(self):
        position = self.position
        self.position = None
        return position

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