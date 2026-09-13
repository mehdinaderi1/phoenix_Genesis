from core.market_data.observer import RealMarketObserver


class RealMarketObserverRuntime:
    def __init__(self, observer):
        if observer is None:
            raise ValueError("observer must not be None")

        self.observer = observer

    def run(self, symbol="BTCUSDT", cycles=1):
        if cycles <= 0:
            raise ValueError("cycles must be greater than zero")

        observations = []

        for _ in range(cycles):
            observation = self.observer.observe(symbol)
            observations.append(observation)
            self._print_observation(observation)

        return observations

    @staticmethod
    def _print_observation(observation):
        source = observation.source or "NONE"
        print(
            f"[OBSERVE] {observation.symbol} "
            f"#{observation.observation_number} "
            f"price={observation.price} "
            f"source={source} "
            f"fallback={observation.fallback_used} "
            f"status={observation.source_status}"
        )
