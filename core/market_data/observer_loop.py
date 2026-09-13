from core.market_data.observer import MarketObservation


class RealMarketObservationLoop:
    def __init__(self, observer):
        if observer is None:
            raise ValueError("observer must not be None")

        self.observer = observer

    def run(self, symbol="BTCUSDT", cycles=1):
        if cycles <= 0:
            raise ValueError("cycles must be greater than zero")

        observations = []

        for _ in range(cycles):
            observations.append(self.observer.observe(symbol))

        return observations
