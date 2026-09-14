from core.database import DatabaseManager
from core.market_data.market_data import MarketData
from core.market_data.observer import RealMarketObserver
from core.market_data.operational_market_context_runtime import OperationalMarketContextRuntime
from core.market_data.operational_paper_runtime import OperationalPaperRuntime
from core.market_data.pipeline import MarketDataPipeline
from exchanges.exchange_manager import ExchangeManager
from exchanges.mock_exchange import MockExchange
from execution.paper_trading_runtime import PaperTradingRuntime
from execution.paper_trading_session import PaperTradingSession
from intelligence.flow import IntelligenceFlow


class ChangingSourceManager:
    def __init__(self):
        self.prices = [65000.0, 64000.0, 63000.0]
        self.index = 0

    def get_price(self, symbol):
        price = self.prices[min(self.index, len(self.prices) - 1)]
        self.index += 1
        return MarketData(
            symbol=symbol,
            price=price,
            source="prototype",
            fallback_used=False,
            source_status="HEALTHY",
        )


class ChangingMarketExchange(MockExchange):
    def __init__(self):
        super().__init__()
        self.sequences = {
            "30m": [66000.0, 64000.0, 63000.0],
            "4H": [66000.0, 64000.0, 63000.0],
            "1D": [66000.0, 64000.0, 63000.0],
        }

        for timeframe, prices in self.sequences.items():
            candles = []
            for index, price in enumerate(prices):
                candles.append({
                    "timestamp": 100 + index,
                    "open": price,
                    "high": price + 100.0,
                    "low": price - 100.0,
                    "close": price,
                    "volume": 10.0 + index
                })
            self.set_candle_sequence(
                "BTCUSDT",
                timeframe,
                candles
            )


def seed_baseline(database):
    for timeframe in ("30m", "4H", "1D"):
        for index in range(5):
            price = 65000.0
            database.connection.execute(
                "INSERT INTO market_candles "
                "(symbol, timeframe, timestamp, open, high, low, close, volume) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    "BTCUSDT",
                    timeframe,
                    index + 1,
                    price,
                    price + 100.0,
                    price - 100.0,
                    price,
                    10.0
                )
            )

    database.connection.commit()


class RecordingIntelligenceFlow(IntelligenceFlow):
    def __init__(self):
        super().__init__()
        self.consensus_history = []
        self.report_history = []

    def create_report(self, consensus):
        self.consensus_history.append(consensus)
        report = super().create_report(consensus)
        self.report_history.append(report)
        return report


def test_operational_prototype_market_state_reaches_intelligence_and_decision(tmp_path):
    database = DatabaseManager(str(tmp_path / "prototype.db"))
    database.connect()
    seed_baseline(database)

    exchange = ChangingMarketExchange()
    exchange_manager = ExchangeManager()
    exchange_manager.set_exchange(exchange)

    pipeline = MarketDataPipeline(
        exchange_manager,
        database,
    )

    observer = RealMarketObserver(ChangingSourceManager())

    market_runtime = OperationalMarketContextRuntime(
        observer=observer,
        market_data_pipeline=pipeline,
        database=database,
    )

    intelligence = RecordingIntelligenceFlow()
    intelligence.enable_inline_outcome_learning = False

    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=1.0,
    )

    paper_runtime = PaperTradingRuntime(session)

    runtime = OperationalPaperRuntime(
        market_context_runtime=market_runtime,
        intelligence_flow=intelligence,
        paper_trading_runtime=paper_runtime
    )

    results = runtime.run(
        symbol="BTCUSDT",
        cycles=3
    )

    assert len(results) == 3
    assert len(intelligence.consensus_history) == 3
    assert len(intelligence.report_history) == 3

    consensus_trends = [
        consensus.trend
        for consensus in intelligence.consensus_history
    ]

    consensus_signals = [
        consensus.signal
        for consensus in intelligence.consensus_history
    ]

    decision_actions = [
        getattr(result["decision"], "action", None)
        for result in results
    ]

    proposal_actions = [
        getattr(result["action_proposal"], "action", None)
        for result in results
    ]

    assert consensus_trends[0] == "BULLISH"
    assert consensus_trends[1] == "BEARISH"
    assert consensus_trends[2] == "BEARISH"

    assert consensus_trends[0] != consensus_trends[1]

    assert len(set(decision_actions)) > 0
    assert len(set(proposal_actions)) > 0

    for result in results:
        assert result["paper_result"] is not None

    database.close()
