from dataclasses import dataclass


@dataclass(frozen=True)
class OperationalCycleResult:
    status: str
    result: object = None
    error: str | None = None


class OperationalLoop:
    """Runs operational cycles while isolating individual cycle failures."""

    def __init__(self, cycle):
        if cycle is None:
            raise ValueError("cycle must not be None")

        self.cycle = cycle

    def run(self, inputs):
        results = []

        for cycle_input in inputs:
            try:
                result = self.cycle.process(
                    action_proposal=cycle_input["action_proposal"],
                    price=cycle_input["price"],
                    symbol=cycle_input.get("symbol", "BTCUSDT"),
                    decision=cycle_input.get("decision"),
                )
            except Exception as exc:
                results.append(
                    OperationalCycleResult(
                        status="ERROR",
                        error=str(exc),
                    )
                )
                continue

            results.append(
                OperationalCycleResult(
                    status="SUCCESS",
                    result=result,
                )
            )

        return results
