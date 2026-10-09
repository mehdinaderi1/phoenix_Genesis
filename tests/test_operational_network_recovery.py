from types import SimpleNamespace

from core.database import DatabaseManager
from core.market_data.operational_market_context import (
    OperationalMarketContext,
)
from core.market_data.operational_market_context_runtime import (
    OperationalMarketContextRuntime,
)
from core.market_data.operational_paper_runtime import (
    OperationalPaperRuntime,
)
from core.market_data.source_manager import MarketDataSourceManager
from core.market_data.source_candle_pipeline import SourceCandlePipeline
from execution.paper_trading_runtime import PaperTradingRuntime
from execution.paper_trading_session import PaperTradingSession


class ReconnectingSource:
    def __init__(self):
        self.candle_calls = 0

    def health_check(self):
        return True

    def get_candle(self, symbol, timeframe="1m"):
        self.candle_calls += 1

        if self.candle_calls == 1:
            raise OSError("simulated network disconnect")

        return {
            "timestamp": 2001,
            "open": 65000.0,
            "high": 65100.0,
            "low": 64900.0,
            "close": 65050.0,
            "volume": 12.0,
        }


class StableObserver:
    def observe(self, symbol, _health_cache=None):
        return SimpleNamespace(
            symbol=symbol,
            price=65050.0,
            source="test-observer",
            fallback_used=False,
            source_status="HEALTHY",
            timestamp="test",
        )


class StableIntelligenceFlow:
    def create_report(self, consensus):
        decision = SimpleNamespace(
            action="WAIT",
            reason="network recovery test",
            confidence=80.0,
        )

        proposal = SimpleNamespace(
            action="WAIT",
            status="APPROVED",
            reason="network recovery test",
            confidence=80.0,
            symbol="BTCUSDT",
            strategy=None,
            risk_status="LOW",
            metadata={},
        )

        return SimpleNamespace(
            decision=decision,
            action_proposal=proposal,
        )


def test_operational_runtime_recovers_on_next_cycle_after_network_failure(
    tmp_path,
):
    database = DatabaseManager(
        db_path=str(tmp_path / "network_recovery.db")
    )
    database.connect()

    try:
        source = ReconnectingSource()
        source_manager = MarketDataSourceManager({"xt": source})
        source_pipeline = SourceCandlePipeline(
            source_manager,
            database,
        )

        market_runtime = OperationalMarketContextRuntime(
            observer=StableObserver(),
            database=database,
            source_candle_pipeline=source_pipeline,
        )

        market_runtime.context_pipeline.build = (
            lambda symbol, timeframes=None: OperationalMarketContext(
                symbol=symbol,
                trend="NEUTRAL",
                signal="WAIT",
                confidence=80.0,
                timestamp="test",
            )
        )

        session = PaperTradingSession(initial_balance=1000.0)
        paper_runtime = PaperTradingRuntime(session=session)

        runtime = OperationalPaperRuntime(
            market_context_runtime=market_runtime,
            intelligence_flow=StableIntelligenceFlow(),
            paper_trading_runtime=paper_runtime,
        )

        results = runtime.run(
            symbol="BTCUSDT",
            cycles=2,
            continue_on_error=True,
            timeframes=("30m",),
        )

        assert len(results) == 2
        assert source.candle_calls == 2

        # Cycle 1: candle fetch failed; no context or paper execution.
        assert results[0]["market_context"] is None
        assert results[0]["paper_result"] is None
        assert results[0]["error"] is None

        # Cycle 2: the same source recovered and processing reached Paper.
        assert results[1]["market_context"] is not None
        assert results[1]["intelligence_context"] is not None
        assert results[1]["report"] is not None
        assert results[1]["paper_result"] is not None
        assert results[1]["error"] is None

        stored_candles = database.get_candles()
        assert len(stored_candles) == 1
        assert stored_candles[0][1] == "BTCUSDT"
        assert stored_candles[0][2] == "30m"
        assert stored_candles[0][7] == 65050.0

    finally:
        database.close()
