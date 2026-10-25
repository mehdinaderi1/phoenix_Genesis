from dataclasses import asdict, dataclass
from typing import Any


VALID_STATES = {
    "BUY",
    "SELL",
    "NO_SIGNAL",
    "NOT_EVALUATED",
    "DATA_ERROR",
}


@dataclass(frozen=True)
class StrategySignal:
    strategy: str
    timeframe: str
    state: str
    confidence: float | None = None
    timestamp: str | None = None
    reasons: tuple[str, ...] = ()
    data_valid: bool = True
    diagnostic_code: str | None = None

    def __post_init__(self):
        if self.state not in VALID_STATES:
            raise ValueError(
                f"Unsupported signal state: {self.state}"
            )

        if not self.strategy.strip():
            raise ValueError("strategy must not be empty")

        if not self.timeframe.strip():
            raise ValueError("timeframe must not be empty")

        if self.confidence is not None and not 0 <= self.confidence <= 100:
            raise ValueError("confidence must be between 0 and 100")

        if self.state == "DATA_ERROR" and self.data_valid:
            object.__setattr__(self, "data_valid", False)


@dataclass(frozen=True)
class EntryAuthorization:
    authorized: bool
    block_reasons: tuple[str, ...] = ()


class SignalMatrix:
    """Experimental reporting layer; it does not execute orders."""

    def __init__(self):
        self._signals: list[StrategySignal] = []

    def add(self, signal: StrategySignal) -> None:
        self._signals.append(signal)

    def all_signals(self) -> list[StrategySignal]:
        return list(self._signals)

    def for_timeframe(self, timeframe: str) -> list[StrategySignal]:
        return [
            signal
            for signal in self._signals
            if signal.timeframe == timeframe
        ]

    def for_strategy(self, strategy: str) -> list[StrategySignal]:
        return [
            signal
            for signal in self._signals
            if signal.strategy == strategy
        ]

    def to_records(self) -> list[dict[str, Any]]:
        return [
            asdict(signal)
            for signal in self._signals
        ]
