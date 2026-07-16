from dataclasses import dataclass


@dataclass
class PerformanceRecord:
    strategy: str
    profit_loss: float
    success: bool