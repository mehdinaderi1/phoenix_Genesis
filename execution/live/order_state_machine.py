"""
Order state machine — models XT order lifecycle.
"""
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    NEW = "NEW"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    UNKNOWN = "UNKNOWN"

    @property
    def is_terminal(self) -> bool:
        return self in (
            OrderStatus.FILLED, OrderStatus.CANCELLED,
            OrderStatus.REJECTED, OrderStatus.EXPIRED,
        )

    @property
    def is_successful(self) -> bool:
        return self == OrderStatus.FILLED


@dataclass
class OrderSnapshot:
    order_id: str
    symbol: str
    side: str
    status: OrderStatus
    price: float
    quantity: float
    filled_quantity: float = 0.0
    avg_fill_price: float = 0.0
    raw: dict = field(default_factory=dict)

    @property
    def remaining_quantity(self) -> float:
        return max(0.0, self.quantity - self.filled_quantity)

    @property
    def notional(self) -> float:
        return self.quantity * self.price

    @property
    def filled_notional(self) -> float:
        return self.filled_quantity * self.avg_fill_price


def parse_xt_status(xt_state) -> OrderStatus:
    if xt_state is None:
        return OrderStatus.UNKNOWN
    m = {
        "NEW": OrderStatus.NEW,
        "PARTIALLY_FILLED": OrderStatus.PARTIALLY_FILLED,
        "PARTIALLY_CANCELED": OrderStatus.PARTIALLY_FILLED,
        "FILLED": OrderStatus.FILLED,
        "CANCELED": OrderStatus.CANCELLED,
        "CANCELLED": OrderStatus.CANCELLED,
        "REJECTED": OrderStatus.REJECTED,
        "EXPIRED": OrderStatus.EXPIRED,
    }
    return m.get(str(xt_state).upper(), OrderStatus.UNKNOWN)


def snapshot_from_xt(data: dict) -> OrderSnapshot:
    return OrderSnapshot(
        order_id=str(data.get("orderId", "")),
        symbol=data.get("symbol"),
        side=(data.get("side") or "").upper(),
        status=parse_xt_status(data.get("state") or data.get("status")),
        price=float(data.get("price") or 0),
        quantity=float(data.get("origQty") or data.get("quantity") or 0),
        filled_quantity=float(data.get("executedQty") or data.get("filledQty") or 0),
        avg_fill_price=float(data.get("avgPrice") or 0),
        raw=data,
    )