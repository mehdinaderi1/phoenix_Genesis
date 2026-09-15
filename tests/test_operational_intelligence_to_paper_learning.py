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
            decision=SimpleNamespace(
                action=action,
                signal=action,
                confidence=85.0,
            ),
            action_proposal=SimpleNamespace(action=action),
        )


class RecordingOutcomeBridge:
    def __init__(self):
        self.calls = []

    def process(self, decision, entry_price, exit_price):
        self.calls.append(
            {
                "decision": decision,
                "entry_price": entry_price,
                "exit_price": exit_price,
            }
        )
        return {"status": "LEARNED"}


def test_operational_intelligence_to_paper_close_produces_outcome_learning():
    intelligence_runtime = OperationalIntelligenceRuntime(
        market_context_runtime=FakeMarketContextRuntime(),
        intelligence_flow=FakeIntelligenceFlow(),
    )

    intelligence_results = intelligence_runtime.run(
        symbol="BTCUSDT",
        cycles=2,
    )

    outcome_bridge = RecordingOutcomeBridge()

    session = PaperTradingSession(
        initial_balance=1000.0,
        outcome_bridge=outcome_bridge,
    )

    paper_runtime = PaperTradingRuntime(session=session)

    cycle_inputs = [
        {
            "action_proposal": result["action_proposal"],
            "price": price,
            "symbol": "BTCUSDT",
            "decision": result["decision"],
        }
        for result, price in zip(
            intelligence_results,
            [65000.0, 66000.0],
        )
    ]

    paper_results = paper_runtime.run(
        cycle_inputs,
        symbol="BTCUSDT",
    )

    assert [result["action"] for result in paper_results] == [
        "OPEN",
        "CLOSE",
    ]

    assert paper_results[1]["learning_result"] == {
        "status": "LEARNED"
    }

    assert len(outcome_bridge.calls) == 1

    call = outcome_bridge.calls[0]

    assert call["decision"] is intelligence_results[0]["decision"]
    assert call["entry_price"] == 65000.0
    assert call["exit_price"] == 66000.0

    assert session.get_position() is None
    assert session.get_trade_count() == 1
