from analysis.multi_timeframe_pipeline import MultiTimeframePipeline
from core.market_data.operational_market_context_builder import OperationalMarketContextBuilder


class OperationalMarketContextPipeline:
    def __init__(self, database):
        self.mtf_pipeline = MultiTimeframePipeline(database)
        self.context_builder = OperationalMarketContextBuilder()

    def build(self, symbol="BTCUSDT"):
        consensus = self.mtf_pipeline.analyze(symbol)
        return self.context_builder.build(symbol, consensus)
