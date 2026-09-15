from types import SimpleNamespace

from core.market_data.operational_intelligence_runtime import (
    OperationalIntelligenceRuntime,
)
from execution.paper_trading_runtime import PaperTradingRuntime
from execution.paper_trading_session import PaperTradingSession


class FakeMarketContextRuntime:
    def run(self, symbol="BTCUSDT", cycles=1):
        return [
            SimpleNamespace(
                symbol=symbol,
                trend="BULLISH" if index == 0 else "BEARISH",
                signal="BUY" if index == 0 else "SELL",
                confidence=85.0,
            )
            for index in range(cycles)
        ]


class FakeIntelligenceFlow:
    def __init__(self):
        self.actions = ["BUY", "SELL"]
        self.index = 0

    def create_report(self, consensus):
        action = self.actions[self.index]
        self.index += 1

        return SimpleNamespace(
            decision=SimpleNamespace(action=action),
            action_proposal=SimpleNamespace(action=action),
        )


def test_operational_intelligence_to_paper_runtime_closes_opposite_position():
    intelligence_runtime = OperationalIntelligenceRuntime(
        market_context_runtime=FakeMarketContextRuntime(),
        intelligence_flow=FakeIntelligenceFlow(),
    )

    intelligence_results = intelligence_runtime.run(
        symbol="BTCUSDT",
        cycles=2,
    )

    assert len(intelligence_results) == 2
    assert [
        result["action_proposal"].action
        for result in intelligence_results
    ] == ["BUY", "SELL"]

    session = PaperTradingSession(initial_balance=1000.0)
    paper_runtime = PaperTradingRuntime(session=session)

    cycle_inputs = [
        {
            "action_proposal": intelligence_results[0]["action_proposal"],
            "price": 65000.0,
            "symbol": "BTCUSDT",
            "decision": intelligence_results[0]["decision"],
        },
        {
            "action_proposal": intelligence_results[1]["action_proposal"],
            "price": 66000.0,
            "symbol": "BTCUSDT",
            "decision": intelligence_results[1]["decision"],
        },
    ]

    paper_results = paper_runtime.run(
        cycle_inputs,
        symbol="BTCUSDT",
    )

    assert len(paper_results) == 2
    assert paper_results[0]["action"] == "OPEN"
    assert paper_results[1]["action"] == "CLOSE"

    assert paper_results[1]["realized_pnl"] > 0
    assert session.get_position() is None
    assert session.get_trade_count() == 1
    assert session.get_total_pnl() > 0
