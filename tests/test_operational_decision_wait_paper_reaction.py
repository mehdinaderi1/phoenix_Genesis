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


class FixedWaitSourceManager:
    def get_price(self, symbol):
        return MarketData(
            symbol=symbol,
            price=65000.0,
            source="prototype",
            fallback_used=False,
            source_status="HEALTHY"
        )


class WaitIntelligenceFlow(IntelligenceFlow):
    def create_report(self, consensus):
        return super().create_report(consensus)


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


def test_operational_decision_wait_reacts_as_paper_hold(tmp_path):
    database = DatabaseManager(str(tmp_path / "prototype.db"))
    database.connect()
    seed_market(database)

    exchange = MockExchange()
    exchange_manager = ExchangeManager()
    exchange_manager.set_exchange(exchange)

    pipeline = MarketDataPipeline(exchange_manager, database)
    observer = RealMarketObserver(FixedWaitSourceManager())

    market_runtime = OperationalMarketContextRuntime(
        observer=observer,
        market_data_pipeline=pipeline,
        database=database
    )

    intelligence = WaitIntelligenceFlow()
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

    for result in results:
        assert result["decision"].action == "WAIT"
        assert result["action_proposal"].action == "WAIT"
        assert result["translated_action_proposal"].action == "WAIT"
        assert result["paper_result"]["action"] == "HOLD"
        assert result["paper_result"]["position"] is None
        assert result["paper_result"]["realized_pnl"] == 0.0

    summary = runtime.build_summary(results)

    assert summary["cycles_processed"] == 3
    assert summary["open_count"] == 0
    assert summary["hold_count"] == 3
    assert summary["close_count"] == 0
    assert summary["trade_count"] == 0
    assert summary["total_pnl"] == 0.0

    print("PAPER REACTION")
    print("  cycles={}".format(summary["cycles_processed"]))
    print("  hold={}".format(summary["hold_count"]))
    print("  position={}".format(summary["current_position"]))
    print("  pnl={}".format(summary["total_pnl"]))

    database.close()
