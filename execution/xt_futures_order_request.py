from dataclasses import dataclass


@dataclass(frozen=True)
class XTFuturesOrderRequest:
    """Validated XT USDT-M Futures order request contract."""

    symbol: str
    order_side: str
    position_side: str
    order_type: str
    quantity: float
    price: float | None = None

    def __post_init__(self):
        if not self.symbol:
            raise ValueError("symbol is required")

        if self.order_side not in ("BUY", "SELL"):
            raise ValueError("order_side must be BUY or SELL")

        if self.position_side not in ("LONG", "SHORT"):
            raise ValueError("position_side must be LONG or SHORT")

        if self.order_type not in ("MARKET", "LIMIT"):
            raise ValueError("order_type must be MARKET or LIMIT")

        if self.quantity <= 0:
            raise ValueError("quantity must be greater than zero")

        if self.order_type == "LIMIT" and (
            self.price is None or self.price <= 0
        ):
            raise ValueError(
                "LIMIT orders require a positive price"
            )

    def to_dict(self):
        data = {
            "symbol": self.symbol,
            "orderSide": self.order_side,
            "positionSide": self.position_side,
            "orderType": self.order_type,
            "origQty": self.quantity,
        }

        if self.price is not None:
            data["price"] = self.price

        return data

