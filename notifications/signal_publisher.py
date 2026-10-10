import hashlib
from datetime import datetime, timezone


class SignalPublisher:
    """Convert an approved operational proposal into a durable signal record."""

    def __init__(self, outbox, primary_timeframe="5m"):
        if not primary_timeframe:
            raise ValueError("primary_timeframe must not be empty")
        self.outbox = outbox
        self.primary_timeframe = str(primary_timeframe)

    @staticmethod
    def _utc_timestamp(value=None):
        if value is None:
            raise ValueError("Signal timestamp is required")

        if isinstance(value, (int, float)):
            value = datetime.fromtimestamp(value, tz=timezone.utc)
        elif isinstance(value, str):
            text = value.strip()
            if not text:
                raise ValueError("Signal timestamp must not be empty")

            if text.isdigit() or (
                text.startswith("-") and text[1:].isdigit()
            ):
                value = datetime.fromtimestamp(int(text), tz=timezone.utc)
            else:
                value = datetime.fromisoformat(text.replace("Z", "+00:00"))

        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Signal timestamp must include a timezone")

        return value.astimezone(timezone.utc).isoformat(
            timespec="seconds"
        ).replace("+00:00", "Z")

    def _get_candle_start(self, candle_boundaries):
        if not isinstance(candle_boundaries, dict):
            return None

        boundary = candle_boundaries.get(self.primary_timeframe)
        if not isinstance(boundary, dict):
            return None

        candle_start = boundary.get("candle_start")
        if candle_start is None:
            return None

        return self.primary_timeframe, str(candle_start)

    def publish(
        self,
        proposal,
        observation,
        candle_boundaries=None,
        generated_at=None,
    ):
        if proposal is None or observation is None:
            return None

        action = getattr(proposal, "action", None)
        status = getattr(proposal, "status", None)
        symbol = getattr(observation, "symbol", None)
        price = getattr(observation, "price", None)
        observation_timestamp = getattr(observation, "timestamp", None)

        if action not in {"BUY", "SELL"} or status != "APPROVED":
            return None
        if not symbol or price is None:
            return None

        try:
            reference_price = float(price)
            observed_at = self._utc_timestamp(observation_timestamp)
            signal_generated_at = self._utc_timestamp(
                generated_at if generated_at is not None
                else observation_timestamp
            )
        except (TypeError, ValueError, OverflowError, OSError):
            return None

        if reference_price <= 0:
            return None

        candle = self._get_candle_start(candle_boundaries)
        if candle is None:
            return None

        timeframe, candle_start = candle
        try:
            normalized_candle_start = self._utc_timestamp(candle_start)
        except (TypeError, ValueError, OverflowError, OSError):
            return None

        identity = "|".join((str(symbol), action, timeframe, candle_start))
        signal_id = "sig-" + hashlib.sha256(
            identity.encode("utf-8")
        ).hexdigest()[:24]

        signal = {
            "signal_id": signal_id,
            "symbol": str(symbol),
            "action": action,
            "status": status,
            "reference_price": reference_price,
            "observed_at": observed_at,
            "generated_at": signal_generated_at,
            "candle_start": normalized_candle_start,
            "timeframe": timeframe,
            "reason": str(getattr(proposal, "reason", "") or ""),
            "confidence": getattr(proposal, "confidence", None),
            "risk_status": getattr(proposal, "risk_status", None),
        }

        message = "\n".join([
            f"Phoenix Genesis signal: {signal_id}",
            f"Symbol: {signal['symbol']}",
            f"Direction: {action}",
            f"Reference price: {reference_price}",
            f"Timeframe: {timeframe}",
            f"Observed at (UTC): {observed_at}",
            f"Generated at (UTC): {signal_generated_at}",
            f"Candle start (UTC): {normalized_candle_start}",
            f"Reason: {signal['reason'] or 'Not provided'}",
            f"Confidence: {signal['confidence']}",
            f"Risk status: {signal['risk_status']}",
            "Mode: OBSERVE / PAPER - no real orders",
        ])

        try:
            self.outbox.record_signal(signal, message)
        except Exception as exc:
            # The signal ID is the idempotency boundary for a candle.
            if type(exc).__name__ != "IntegrityError":
                raise

            existing = self.outbox.get_signal(signal_id)
            existing_message = self.outbox.get_message(signal_id)
            if not existing or not existing_message:
                raise

            # Decision content must match. Market observations and
            # publication timestamps remain those of the first record.
            decision_fields = (
                "signal_id",
                "symbol",
                "action",
                "status",
                "candle_start",
                "timeframe",
                "reason",
                "confidence",
                "risk_status",
            )
            if any(existing.get(key) != signal.get(key) for key in decision_fields):
                raise

            return existing

        return signal

