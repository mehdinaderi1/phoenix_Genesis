from types import SimpleNamespace

from core.market_data.operational_paper_runtime import (
    OperationalPaperRuntime,
)
from execution.xt_futures_shadow_execution_runtime import (
    XTFuturesShadowExecutionRuntime,
)


class FakeMarketContextRuntime:
    def run_cycle(self, symbol="BTCUSDT", timeframes=None):
        return {
            "observation": SimpleNamespace(
                symbol=symbol,
                price=50000.0,
                source="mock",
                fallback_used=False,
                source_status="HEALTHY",
            ),
            "context": SimpleNamespace(
                symbol=symbol,
                trend="BULLISH",
                signal="BUY",
                confidence=90.0,
                timestamp="2026-10-02T00:00:00+00:00",
            ),
            "candle_boundaries": {},
        }


class FakeIntelligenceFlow:
    def create_report(self, consensus):
        return SimpleNamespace(
            decision=SimpleNamespace(action="BUY"),
            action_proposal=SimpleNamespace(
                action="BUY",
                status="APPROVED",
                symbol="BTCUSDT",
            ),
        )


class FakePaperTradingRuntime:
    def __init__(self):
        self.cycles = []

    def run(self, cycles, symbol="BTCUSDT"):
        self.cycles.extend(cycles)

        return [{
            "action": "OPEN",
            "position": SimpleNamespace(
                side="BUY",
                entry_price=cycles[0]["price"],
            ),
            "realized_pnl": 0.0,
            "learning_result": None,
        }]


def test_operational_runtime_reaches_real_shadow_preparation():
    market_runtime = FakeMarketContextRuntime()
    intelligence = FakeIntelligenceFlow()
    paper_runtime = FakePaperTradingRuntime()

    shadow_runtime = XTFuturesShadowExecutionRuntime(
        balance=1000.0,
        position_size_percent=1.0,
        transport=None,
        request_builder=None,
    )

    runtime = OperationalPaperRuntime(
        market_context_runtime=market_runtime,
        intelligence_flow=intelligence,
        paper_trading_runtime=paper_runtime,
        shadow_execution_runtime=shadow_runtime,
    )

    results = runtime.run(
        symbol="BTCUSDT",
        cycles=1,
    )

    assert len(results) == 1

    result = results[0]

    assert result["error"] is None

    assert result["paper_result"]["action"] == "OPEN"

    shadow_result = result["shadow_result"]

    assert shadow_result is not None
    assert shadow_result["status"] == "PREPARED"
    assert shadow_result["execution"] is None

    assert shadow_result["prepared"] is not None

    assert shadow_result["request"].symbol == "BTCUSDT"
    assert shadow_result["request"].order_side == "BUY"
    assert shadow_result["request"].position_side == "LONG"

    assert shadow_result["payload"]["origQty"] == 0.0002

    assert shadow_result["idempotency_key"] is not None
