from types import SimpleNamespace

from core.market_data.operational_market_context import OperationalMarketContext
from core.market_data.operational_paper_runtime import OperationalPaperRuntime
from execution.paper_trading_runtime import PaperTradingRuntime
from execution.paper_trading_session import PaperTradingSession
from intelligence.flow import IntelligenceFlow


class FakeOperationalMarketContextRuntime:
    def __init__(self):
        self.calls = 0

    def run_cycle(self, symbol="BTCUSDT"):
        self.calls += 1

        observation = SimpleNamespace(
            symbol=symbol,
            price=65000.0,
            source="mock",
            fallback_used=False,
            source_status="HEALTHY"
        )

        context = OperationalMarketContext(
            symbol=symbol,
            trend="BULLISH",
            signal="BUY",
            confidence=85.0,
            timestamp="2026-09-13T00:00:00+00:00"
        )

        return {
            "observation": observation,
            "context": context
        }


def test_operational_paper_runtime_uses_real_intelligence_and_paper_runtime():
    market_runtime = FakeOperationalMarketContextRuntime()

    intelligence = IntelligenceFlow()
    intelligence.enable_inline_outcome_learning = False

    session = PaperTradingSession()
    paper_runtime = PaperTradingRuntime(session)

    runtime = OperationalPaperRuntime(
        market_runtime,
        intelligence,
        paper_runtime
    )

    results = runtime.run(cycles=1)

    assert len(results) == 1
    assert market_runtime.calls == 1

    result = results[0]

    assert result["observation"].price == 65000.0
    assert result["market_context"].trend == "BULLISH"

    assert result["report"] is not None
    assert result["decision"] is not None
    assert result["decision"].action == "PREPARE_LONG"
    assert result["action_proposal"] is not None
    assert result["action_proposal"].action == "PREPARE_LONG"
    assert result["action_proposal"].status == "APPROVED"

    paper_result = result["paper_result"]
    assert paper_result["action"] == "OPEN"
    assert paper_result["position"] is not None

    assert session.get_position() is not None
    assert session.get_trade_count() == 0
    assert session.get_total_pnl() == 0.0
