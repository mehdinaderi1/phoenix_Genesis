from dataclasses import dataclass
import hashlib
import json


@dataclass(frozen=True)
class XTFuturesIdempotencyKey:
    """Deterministic identity for one XT Futures execution attempt."""

    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("idempotency key is required")


class XTFuturesIdempotencyKeyBuilder:
    """
    Builds a deterministic identity for one XT Futures execution attempt.

    Same logical request + same attempt identity -> same key.
    Changing an order-defining field or attempt identity -> different key.

    When attempt_identity is None, the legacy logical-order identity is
    preserved for backward compatibility.
    """

    def build(
        self,
        symbol,
        order_side,
        position_side,
        order_type,
        quantity,
        price=None,
        attempt_identity=None,
    ):
        payload = {
            "symbol": symbol,
            "order_side": order_side,
            "position_side": position_side,
            "order_type": order_type,
            "quantity": quantity,
            "price": price,
        }

        if attempt_identity is not None:
            payload["attempt_identity"] = attempt_identity

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