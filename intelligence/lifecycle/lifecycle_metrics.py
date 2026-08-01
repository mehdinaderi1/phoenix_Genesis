from dataclasses import dataclass


@dataclass
class LifecycleMetrics:

    strategy_name: str

    total_events: int

    transitions: int

    current_state: str

    lifecycle_score: float

    health: str