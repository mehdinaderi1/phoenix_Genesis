from dataclasses import dataclass

from core.market_data.cross_source_validator import CrossSourceValidationResult
from core.market_data.operational_market_context import OperationalMarketContext


@dataclass(frozen=True)
class ValidatedMarketContext:
    context: OperationalMarketContext
    validation: CrossSourceValidationResult

    @property
    def symbol(self):
        return self.context.symbol

    @property
    def trend(self):
        return self.context.trend

    @property
    def signal(self):
        return self.context.signal

    @property
    def confidence(self):
        return self.context.confidence

    @property
    def timestamp(self):
        return self.context.timestamp

    def summary(self):
        return {
            "symbol": self.symbol,
            "trend": self.trend,
            "signal": self.signal,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
            "validation": {
                "status": self.validation.status,
                "primary_source": self.validation.primary_source,
                "reference_source": self.validation.reference_source,
                "price": self.validation.price,
                "difference_percent": self.validation.difference_percent,
            },
        }
