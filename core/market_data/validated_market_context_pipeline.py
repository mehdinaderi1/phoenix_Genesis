from core.market_data.operational_market_context_pipeline import OperationalMarketContextPipeline


class ValidatedMarketContextPipeline:
    """Builds market context only when cross-source validation permits it."""

    ALLOWED_STATUSES = {"VALID", "INSUFFICIENT"}

    def __init__(self, database, validation_pipeline):
        if database is None:
            raise ValueError("database must not be None")

        if validation_pipeline is None:
            raise ValueError("validation_pipeline must not be None")

        self.validation_pipeline = validation_pipeline
        self.context_pipeline = OperationalMarketContextPipeline(database)

    def build(self, symbol="BTCUSDT"):
        validation = self.validation_pipeline.validate(symbol)

        if validation.status not in self.ALLOWED_STATUSES:
            return {
                "validation": validation,
                "context": None
            }

        context = self.context_pipeline.build(symbol)

        return {
            "validation": validation,
            "context": context
        }
