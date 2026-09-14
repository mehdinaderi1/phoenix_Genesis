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
            source_status="HEALTHY"
        )


class ChangingMarketExchange(MockExchange):
    def __init__(self):
        super().__init__()
        for timeframe in ("30m", "4H", "1D"):
            candles = []
            for index, price in enumerate((66000.0, 64000.0, 63000.0)):
                candles.append({
                    "timestamp": 100 + index,
                    "open": price,
                    "high": price + 100.0,
                    "low": price - 100.0,
                    "close": price,
                    "volume": 10.0 + index
                })
            self.set_candle_sequence("BTCUSDT", timeframe, candles)


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
        self.records = []

    def create_report(self, consensus):
        report = super().create_report(consensus)
        self.records.append({
            "consensus_trend": getattr(consensus, "trend", None),
            "consensus_signal": getattr(consensus, "signal", None),
            "consensus_confidence": getattr(consensus, "confidence", None),
            "report_signal": getattr(report, "signal", None),
            "report_trend": getattr(report, "trend", None),
            "report_confidence": getattr(report, "confidence", None),
            "decision_action": getattr(report.decision, "action", None),
            "proposal_action": getattr(report.action_proposal, "action", None),
            "proposal_status": getattr(report.action_proposal, "status", None)
        })
        return report


def test_operational_prototype_decision_reaction(tmp_path):
    database = DatabaseManager(str(tmp_path / "prototype.db"))
    database.connect()
    seed_baseline(database)

    exchange = ChangingMarketExchange()
    exchange_manager = ExchangeManager()
    exchange_manager.set_exchange(exchange)

    pipeline = MarketDataPipeline(exchange_manager, database)
    observer = RealMarketObserver(ChangingSourceManager())

    market_runtime = OperationalMarketContextRuntime(
        observer=observer,
        market_data_pipeline=pipeline,
        database=database
    )

    intelligence = RecordingIntelligenceFlow()
    intelligence.enable_inline_outcome_learning = False

    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=1.0
    )

    paper_runtime = PaperTradingRuntime(session)

    runtime = OperationalPaperRuntime(
        market_context_runtime=market_runtime,
        intelligence_flow=intelligence,
        paper_trading_runtime=paper_runtime
    )

    results = runtime.run(symbol="BTCUSDT", cycles=3)

    assert len(results) == 3
    assert len(intelligence.records) == 3

    first = intelligence.records[0]
    second = intelligence.records[1]
    third = intelligence.records[2]

    assert first["consensus_trend"] == "BULLISH"
    assert second["consensus_trend"] == "BEARISH"
    assert third["consensus_trend"] == "BEARISH"
    assert first["consensus_trend"] != second["consensus_trend"]

    for record in intelligence.records:
        assert record["decision_action"] is not None
        assert record["proposal_action"] is not None

    for index, record in enumerate(intelligence.records, start=1):
        print("DECISION CYCLE {}".format(index))
        print("  trend={}".format(record["consensus_trend"]))
        print("  signal={}".format(record["consensus_signal"]))
        print("  confidence={}".format(record["consensus_confidence"]))
        print("  report_signal={}".format(record["report_signal"]))
        print("  report_trend={}".format(record["report_trend"]))
        print("  decision={}".format(record["decision_action"]))
        print("  proposal={}".format(record["proposal_action"]))
        print("  status={}".format(record["proposal_status"]))

    database.close()
