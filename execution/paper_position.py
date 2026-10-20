from dataclasses import dataclass, field
import os
from datetime import datetime, timezone
from config.settings import Settings


def _fee_rate() -> float:
    market = getattr(Settings, "FEE_MARKET", "futures")
    order_type = getattr(Settings, "FEE_ORDER_TYPE", "taker")
    table = getattr(Settings, f"FEE_{market.upper()}", None) or {}
    return float(table.get(order_type, 0.0))


@dataclass
class PaperPosition:
    symbol: str
    side: str
    entry_price: float
    quantity: float
    decision: object = None
    sl: float | None = None
    tp: float | None = None
    opened_at: str | None = None
    leverage: float = 1.0      # ← اضافه شد

    def notional(self) -> float:
        return self.entry_price * self.quantity

    def margin(self) -> float:
        lev = max(self.leverage, 1.0)
        return self.notional() / lev

    def unrealized_pnl(self, current_price):
        if self.side == "BUY":
            return (current_price - self.entry_price) * self.quantity
        if self.side == "SELL":
            return (self.entry_price - current_price) * self.quantity
        return 0.0

    def fee_breakdown(self, exit_price):
        rate = _fee_rate()
        entry_fee = self.entry_price * self.quantity * rate
        exit_fee = exit_price * self.quantity * rate
        return {
            "rate": rate,
            "entry_fee": entry_fee,
            "exit_fee": exit_fee,
            "total": entry_fee + exit_fee,
        }

    def realized_pnl(self, exit_price):
        gross = self.unrealized_pnl(exit_price)
        fees = self.fee_breakdown(exit_price)
        return gross - fees["total"]

    def should_close_at(self, current_price, now_utc=None):
        if self.sl is not None and self.tp is not None:
            if self.side == "BUY":
                if current_price <= self.sl:
                    return True, "SL", self.sl
                if current_price >= self.tp:
                    return True, "TP", self.tp
            elif self.side == "SELL":
                if current_price >= self.sl:
                    return True, "SL", self.sl
                if current_price <= self.tp:
                    return True, "TP", self.tp

        if self.opened_at is not None:
            max_hours = float(getattr(Settings, "MAX_POSITION_HOURS", 4))
            try:
                opened = datetime.fromisoformat(self.opened_at)
                now = now_utc or datetime.now(timezone.utc)
                if (now - opened).total_seconds() >= max_hours * 3600:
                    return True, "TIMEOUT", current_price
            except (ValueError, TypeError):
                pass
        return False, None, None