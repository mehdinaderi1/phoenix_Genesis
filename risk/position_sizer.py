"""
Position sizer — computes quantity based on risk per trade.
"""
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PositionSize:
    allowed: bool
    quantity: float
    notional: float
    risk_amount: float
    reason: str = ""


class PositionSizer:
    """
    Fixed-fractional sizing based on stop-loss distance.

    Rule:
      risk_amount = current_capital * risk_per_trade_pct / 100
      quantity    = risk_amount / |entry_price - stop_loss|

    Bounds:
      - quantity <= current_capital / entry_price * max_position_pct / 100
    """
    def __init__(
        self,
        risk_per_trade_pct: float = 0.5,
        max_position_pct: float = 2.0,
        min_notional: float = 5.0,
        quantity_precision: int = 5,
        price_precision: int = 2,
    ):
        self.risk_per_trade_pct = risk_per_trade_pct
        self.max_position_pct = max_position_pct
        self.min_notional = min_notional
        self.quantity_precision = quantity_precision
        self.price_precision = price_precision

    def compute(
        self,
        capital: float,
        entry_price: float,
        stop_loss: float,
    ) -> PositionSize:
        if capital <= 0:
            return PositionSize(False, 0, 0, 0, "capital_zero")
        if entry_price <= 0:
            return PositionSize(False, 0, 0, 0, "invalid_entry_price")

        sl_distance = abs(entry_price - stop_loss)
        if sl_distance <= 0:
            return PositionSize(False, 0, 0, 0, "zero_sl_distance")

        risk_amount = capital * self.risk_per_trade_pct / 100.0
        raw_qty = risk_amount / sl_distance

        max_qty_by_position = capital * self.max_position_pct / 100.0 / entry_price
        capped_qty = min(raw_qty, max_qty_by_position)
        capped = raw_qty > max_qty_by_position

        qty = round(capped_qty, self.quantity_precision)
        if qty <= 0:
            return PositionSize(False, 0, 0, risk_amount, "qty_below_precision")

        notional = round(qty * entry_price, self.price_precision)
        if notional < self.min_notional:
            # bump up to minimum, if within position cap
            min_qty = round(self.min_notional / entry_price, self.quantity_precision)
            if min_qty <= max_qty_by_position:
                qty = min_qty
                notional = round(qty * entry_price, self.price_precision)
            else:
                return PositionSize(
                    False, 0, 0, risk_amount,
                    f"notional_{notional}_below_min_{self.min_notional}_and_capped",
                )

        return PositionSize(
            allowed=True,
            quantity=qty,
            notional=notional,
            risk_amount=risk_amount,
            reason="capped_by_position" if capped else "ok",
        )