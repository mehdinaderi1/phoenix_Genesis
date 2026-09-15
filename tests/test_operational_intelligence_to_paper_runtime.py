from types import SimpleNamespace

from execution.paper_trading_runtime import PaperTradingRuntime
from execution.paper_trading_session import PaperTradingSession
from core.market_data.operational_intelligence_runtime import (
    OperationalIntelligenceRuntime,
)


class FakeMarketContextRuntime:
    def __init__(self, signals):
        self.signals = list(signals)

    def run(self, symbol="BTCUSDT", cycles=1):
        return [
            SimpleNamespace(
                symbol=symbol,
                trend="BULLISH",
                signal=self.signals[index],
                confidence=85.0,
            )
            for index in range(cycles)
        ]


class FakeIntelligenceFlow:
    def __init__(self, actions):
        self.actions = list(actions)
        self.index = 0

    def create_report(self, consensus):
        action = self.actions[self.index]
        self.index += 1

        return SimpleNamespace(
            decision=SimpleNamespace(action=action),
            action_proposal=SimpleNamespace(action=action),
        )


def test_operational_intelligence_output_can_feed_paper_trading_runtime():
    intelligence_runtime = OperationalIntelligenceRuntime(
        market_context_runtime=FakeMarketContextRuntime(["BUY"]),
        intelligence_flow=FakeIntelligenceFlow(["BUY"]),
    )

    intelligence_results = intelligence_runtime.run(
        symbol="BTCUSDT",
        cycles=1,
    )

    assert len(intelligence_results) == 1

    result = intelligence_results[0]
    assert result["decision"].action == "BUY"
    assert result["action_proposal"].action == "BUY"

    session = PaperTradingSession(initial_balance=1000.0)
    paper_runtime = PaperTradingRuntime(session=session)

    cycle_input = {
        "action_proposal": result["action_proposal"],
        "price": 65000.0,
        "symbol": "BTCUSDT",
        "decision": result["decision"],
    }

    paper_results = paper_runtime.run(
        [cycle_input],
        symbol="BTCUSDT",
    )

    assert len(paper_results) == 1
    assert paper_results[0]["action"] == "OPEN"
    assert session.get_position() is not None


def test_wait_action_from_intelligence_is_held_by_paper_runtime():
    intelligence_runtime = OperationalIntelligenceRuntime(
        market_context_runtime=FakeMarketContextRuntime(["WAIT"]),
        intelligence_flow=FakeIntelligenceFlow(["WAIT"]),
    )

    intelligence_results = intelligence_runtime.run(
        symbol="BTCUSDT",
        cycles=1,
    )

    assert len(intelligence_results) == 1
    assert intelligence_results[0]["action_proposal"].action == "WAIT"

    session = PaperTradingSession(initial_balance=1000.0)
    paper_runtime = PaperTradingRuntime(session=session)

    cycle_input = {
        "action_proposal": intelligence_results[0]["action_proposal"],
        "price": 65000.0,
        "symbol": "BTCUSDT",
        "decision": intelligence_results[0]["decision"],
    }

    paper_results = paper_runtime.run(
        [cycle_input],
        symbol="BTCUSDT",
    )

    assert len(paper_results) == 1
    assert paper_results[0]["action"] == "HOLD"
    assert session.get_position() is None


def test_operational_intelligence_to_paper_runtime_preserves_state_across_cycles():
    intelligence_runtime = OperationalIntelligenceRuntime(
        market_context_runtime=FakeMarketContextRuntime(
            ["BUY", "WAIT", "WAIT"]
        ),
        intelligence_flow=FakeIntelligenceFlow(
            ["BUY", "WAIT", "WAIT"]
        ),
    )

    intelligence_results = intelligence_runtime.run(
        symbol="BTCUSDT",
        cycles=3,
    )

    assert len(intelligence_results) == 3
    assert [
        result["action_proposal"].action
        for result in intelligence_results
    ] == ["BUY", "WAIT", "WAIT"]

    session = PaperTradingSession(initial_balance=1000.0)
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
            [65000.0, 65500.0, 66000.0],
        )
    ]

    paper_results = paper_runtime.run(
        cycle_inputs,
        symbol="BTCUSDT",
    )

    assert len(paper_results) == 3
    assert [result["action"] for result in paper_results] == [
        "OPEN",
        "HOLD",
        "HOLD",
    ]

    position = session.get_position()

    assert position is not None
    assert position.side == "BUY"
    assert position.entry_price == 65000.0
