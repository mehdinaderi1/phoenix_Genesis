from time import sleep


class OperationalObservationRunner:
    """Repeats an operational runtime with a configurable interval."""

    def __init__(self, runtime, sleep_fn=sleep):
        if runtime is None:
            raise ValueError("runtime must not be None")

        if sleep_fn is None:
            raise ValueError("sleep_fn must not be None")

        self.runtime = runtime
        self.sleep_fn = sleep_fn

    def run(
        self,
        symbol="BTCUSDT",
        cycles=1,
        interval_seconds=0,
        continue_on_error=False
    ):
        if cycles <= 0:
            raise ValueError(
                "cycles must be greater than zero"
            )

        if interval_seconds < 0:
            raise ValueError(
                "interval_seconds must be greater than or equal to zero"
            )

        results = []

        for cycle_number in range(1, cycles + 1):
            cycle_results = self.runtime.run(
                symbol=symbol,
                cycles=1,
                continue_on_error=continue_on_error
            )

            results.extend(cycle_results)

            if cycle_number < cycles and interval_seconds > 0:
                self.sleep_fn(interval_seconds)

        return results
