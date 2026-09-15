from core.market_data.market_data import MarketData


class MarketDataSourceManager:
    """Selects healthy market-data sources with primary/fallback behavior."""

    def __init__(self, sources=None):
        self.sources = {}
        self.primary_source = None
        if sources:
            for name, source in sources.items():
                self.add_source(name, source)

    def add_source(self, name, source):
        if not name:
            raise ValueError("Source name must not be empty")
        if source is None:
            raise ValueError("Source must not be None")
        self.sources[name] = source
        if self.primary_source is None:
            self.primary_source = name

    def set_primary_source(self, name):
        if name not in self.sources:
            raise ValueError(f"Unknown market-data source: {name}")
        self.primary_source = name

    def get_source(self, name):
        return self.sources.get(name)

    def _is_healthy(self, source):
        try:
            return bool(source.health_check())
        except Exception:
            return False

    def get_healthy_sources(self):
        healthy = []
        for name, source in self.sources.items():
            if self._is_healthy(source):
                healthy.append(name)
        return healthy

    def get_prices(self, symbol):
        prices = {}

        for name, source in self.sources.items():
            if not self._is_healthy(source):
                continue

            try:
                price = source.get_price(symbol)
            except Exception:
                continue

            if price is None:
                continue

            prices[name] = float(price)

        return prices

    def get_price(self, symbol):
        if not self.sources:
            raise RuntimeError("No market-data sources configured")

        ordered_names = []
        if self.primary_source:
            ordered_names.append(self.primary_source)
        ordered_names.extend(
            name for name in self.sources
            if name != self.primary_source
        )

        failures = []

        for name in ordered_names:
            source = self.sources[name]
            if not self._is_healthy(source):
                failures.append(name)
                continue

            try:
                price = source.get_price(symbol)
            except Exception:
                failures.append(name)
                continue

            if price is None:
                failures.append(name)
                continue

            return MarketData(
                symbol=symbol,
                price=float(price),
                source=name,
                fallback_used=name != self.primary_source,
                source_status="HEALTHY"
            )

        message = (
            f"No healthy market-data source available for {symbol}. "
            f"Failed sources: {failures}"
        )
        raise RuntimeError(message)
