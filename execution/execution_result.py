from dataclasses import dataclass


@dataclass
class ExecutionResult:
    status: str
    action: str
    symbol: str
    price: float | None = None
    quantity: float | None = None
    reason: str | None = None