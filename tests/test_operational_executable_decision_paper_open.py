from types import SimpleNamespace

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


class FixedSourceManager:
    def health_check(self):
        return True

    def get_price(self, symbol):
        return MarketData(
            symbol=symbol,
            price=65000.0,
            source="prototype",
            fallback_used=False,
            source_status="HEALTHY"
        )


class ExecutableIntelligenceFlow:
    def create_report(self, consensus):
        decision = SimpleNamespace(action="BUY")
        action_proposal = SimpleNamespace(
            action="PREPARE_LONG",
            status="APPROVED",
            reason="Controlled executable test decision",
            confidence=85.0,
            symbol="BTCUSDT",
            strategy=None,
            risk_status="ACCEPTED",
            metadata={}
        )

        return SimpleNamespace(
            signal="BUY",
            trend="BULLISH",
            confidence=85.0,
            regime="TRENDING",
            risk="ACCEPTED",
            decision=decision,
            action_proposal=action_proposal
        )


def seed_market(database):
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


def test_operational_executable_decision_opens_paper_position(tmp_path):
    database = DatabaseManager(str(tmp_path / "prototype.db"))
    database.connect()
    seed_market(database)

    exchange = MockExchange()
    exchange_manager = ExchangeManager()
    exchange_manager.set_exchange(exchange)

    pipeline = MarketDataPipeline(exchange_manager, database)
    observer = RealMarketObserver(FixedSourceManager())

    market_runtime = OperationalMarketContextRuntime(
        observer=observer,
        market_data_pipeline=pipeline,
        database=database
    )

    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=1.0
    )
    paper_runtime = PaperTradingRuntime(session)

    runtime = OperationalPaperRuntime(
        market_context_runtime=market_runtime,
        intelligence_flow=ExecutableIntelligenceFlow(),
        paper_trading_runtime=paper_runtime
    )

    results = runtime.run(symbol="BTCUSDT", cycles=1)

    assert len(results) == 1

    result = results[0]
    assert result["decision"].action == "BUY"
    assert result["action_proposal"].action == "PREPARE_LONG"
    assert result["translated_action_proposal"].action == "BUY"

    paper_result = result["paper_result"]
    assert paper_result["action"] == "OPEN"
    assert paper_result["execution_result"] is not None
    assert paper_result["position"] is not None
    assert paper_result["position"].side == "BUY"
    assert paper_result["position"].entry_price == 65000.0
    assert paper_result["position"].quantity > 0
    assert paper_result["realized_pnl"] == 0.0

    assert session.get_position() is not None
    assert session.get_position().side == "BUY"
    assert session.get_trade_count() == 0
    assert session.get_total_pnl() == 0.0

    print("EXECUTABLE DECISION")
    print("  decision={}".format(result["decision"].action))
    print("  proposal={}".format(result["action_proposal"].action))
    print("  translated={}".format(result["translated_action_proposal"].action))
    print("  paper_action={}".format(paper_result["action"]))
    print("  position_side={}".format(paper_result["position"].side))
    print("  entry_price={}".format(paper_result["position"].entry_price))

    database.close()
