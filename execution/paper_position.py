import os
from dataclasses import dataclass
from datetime import datetime, timezone

from config.settings import Settings


def _fee_rate() -> float:
    market = getattr(Settings, "FEE_MARKET", "futures")
    order_type = os.getenv(
        "PHOENIX_FEE_TYPE",
        getattr(Settings, "FEE_ORDER_TYPE", "taker"),
    )
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
    leverage: float = 1.0
    # ─── Trailing/BE/Partial state ───
    initial_sl: float | None = None
    partial_closed: bool = False
    be_moved: bool = False
    best_price_seen: float | None = None
    realized_partial_pnl: float = 0.0

    def __post_init__(self):
        if self.initial_sl is None and self.sl is not None:
            self.initial_sl = self.sl
        if self.best_price_seen is None:
            self.best_price_seen = self.entry_price

    # ─── محاسبات ───
    def _risk_distance(self) -> float:
        if self.initial_sl is None or self.initial_sl == 0:
            return self.entry_price * 0.01
        return abs(self.entry_price - self.initial_sl)

    def _profit_in_R(self, current_price: float) -> float:
        risk = self._risk_distance()
        if risk <= 0:
            return 0.0
        if self.side == "BUY":
            return (current_price - self.entry_price) / risk
        return (self.entry_price - current_price) / risk

    # ─── Trailing state ───
    def update_best_price(self, current_price: float):
        if self.best_price_seen is None:
            self.best_price_seen = current_price
            return
        if self.side == "BUY" and current_price > self.best_price_seen:
            self.best_price_seen = current_price
        elif self.side == "SELL" and current_price < self.best_price_seen:
            self.best_price_seen = current_price

    # ─── Partial ───
    def should_partial_close(self, current_price: float):
        if not getattr(Settings, "PARTIAL_TP_ENABLED", False):
            return None
        if self.partial_closed:
            return None
        threshold = float(getattr(Settings, "PARTIAL_TP_AT_R", 1.0))
        if self._profit_in_R(current_price) >= threshold:
            return float(getattr(Settings, "PARTIAL_TP_FRACTION", 0.5))
        return None

    # ─── BE + Trailing ───
    def should_move_sl(self, current_price: float):
        if self.sl is None:
            return None
        profit_R = self._profit_in_R(current_price)

        # BE after 1R
        if getattr(Settings, "BE_ENABLED", False) and not self.be_moved:
            be_at = float(getattr(Settings, "PARTIAL_TP_AT_R", 1.0))
            if profit_R >= be_at:
                if self.side == "BUY" and self.sl < self.entry_price:
                    return self.entry_price
                if self.side == "SELL" and self.sl > self.entry_price:
                    return self.entry_price

        # Trailing after 2R
        if getattr(Settings, "TRAILING_ENABLED", False):
            start_R = float(getattr(Settings, "TRAILING_START_R", 2.0))
            if profit_R >= start_R and self.best_price_seen is not None:
                risk = self._risk_distance()
                dist = float(getattr(Settings, "TRAILING_DISTANCE_R", 0.5))
                if self.side == "BUY":
                    candidate = self.best_price_seen - risk * dist
                    if candidate > self.sl and candidate > self.entry_price:
                        return candidate
                else:
                    candidate = self.best_price_seen + risk * dist
                    if candidate < self.sl and candidate < self.entry_price:
                        return candidate
        return None

    # ─── PnL ───
    def unrealized_pnl(self, current_price):
        if self.side == "BUY":
            return (current_price - self.entry_price) * self.quantity
        if self.side == "SELL":
            return (self.entry_price - current_price) * self.quantity
        return 0.0

    def total_pnl(self, current_price):
        return self.unrealized_pnl(current_price) + self.realized_partial_pnl

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