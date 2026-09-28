from dataclasses import dataclass


@dataclass(frozen=True)
class XTFuturesOrderDetailRequest:
    """Validated XT Futures order-detail query contract."""
    order_id: int

    def __post_init__(self):
        if isinstance(self.order_id, bool):
            raise ValueError("order_id must be an integer")

        if not isinstance(self.order_id, int):
            raise ValueError("order_id must be an integer")

        if self.order_id <= 0:
            raise ValueError("order_id must be greater than zero")

    def to_query_params(self):
        return {
            "orderId": self.order_id,
        }
