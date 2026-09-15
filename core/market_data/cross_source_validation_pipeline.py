from core.market_data.cross_source_validator import CrossSourceValidator
from core.market_data.source_manager import MarketDataSourceManager


class CrossSourceValidationPipeline:
    """Connects multi-source market prices to cross-source validation."""

    def __init__(self, source_manager, validator=None):
        if source_manager is None:
            raise ValueError("source_manager must not be None")

        if not isinstance(source_manager, MarketDataSourceManager):
            raise TypeError(
                "source_manager must be a MarketDataSourceManager"
            )

        self.source_manager = source_manager
        self.validator = validator or CrossSourceValidator()

    def validate(self, symbol):
        prices = self.source_manager.get_prices(symbol)
        return self.validator.validate(prices)
