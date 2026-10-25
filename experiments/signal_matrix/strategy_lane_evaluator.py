from dataclasses import dataclass

from experiments.signal_matrix.signal_matrix import (
    SignalMatrix,
    StrategySignal,
)


@dataclass(frozen=True)
class StrategyLane:
    strategy: str
    timeframe: str


class StrategyLaneEvaluator:
    """Collect independent strategy/timeframe results for reporting only."""

    def __init__(self, lanes: list[StrategyLane]):
        keys = [(lane.strategy, lane.timeframe) for lane in lanes]
        if len(keys) != len(set(keys)):
            raise ValueError("Duplicate strategy/timeframe lane")

        self.lanes = tuple(lanes)

    def collect(self, results: dict[tuple[str, str], StrategySignal]):
        matrix = SignalMatrix()

        for lane in self.lanes:
            key = (lane.strategy, lane.timeframe)
            result = results.get(key)

            if result is None:
                matrix.add(
                    StrategySignal(
                        strategy=lane.strategy,
                        timeframe=lane.timeframe,
                        state="NOT_EVALUATED",
                        reasons=("No evaluation result supplied",),
                    )
                )
                continue

            if (
                result.strategy != lane.strategy
                or result.timeframe != lane.timeframe
            ):
                raise ValueError(
                    f"Result identity mismatch for lane {key!r}"
                )

            matrix.add(result)

        return matrix
