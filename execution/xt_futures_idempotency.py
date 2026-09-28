from dataclasses import dataclass
import hashlib
import json


@dataclass(frozen=True)
class XTFuturesIdempotencyKey:
    """Deterministic identity for one logical XT Futures order."""

    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("idempotency key is required")


class XTFuturesIdempotencyKeyBuilder:
    """
    Builds a deterministic identity from the logical order request.

    Same logical request -> same key.
    Any order-defining field change -> different key.
    """

    def build(
        self,
        symbol,
        order_side,
        position_side,
        order_type,
        quantity,
        price=None,
    ):
        payload = {
            "symbol": symbol,
            "order_side": order_side,
            "position_side": position_side,
            "order_type": order_type,
            "quantity": quantity,
            "price": price,
        }

        canonical = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        )

        digest = hashlib.sha256(
            canonical.encode("utf-8")
        ).hexdigest()

        return XTFuturesIdempotencyKey(
            value=digest
        )
