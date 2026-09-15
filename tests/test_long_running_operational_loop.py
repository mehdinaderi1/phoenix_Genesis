from types import SimpleNamespace

from core.market_data.operational_intelligence_runtime import (
    OperationalIntelligenceRuntime,
)
from execution.paper_trading_runtime import PaperTradingRuntime
from execution.paper_trading_session import PaperTradingSession


class FakeMarketContextRuntime:
    def run(self, symbol="BTCUSDT", cycles=1):
        signals = ["BUY", "WAIT", "WAIT", "SELL", "WAIT"]

        return [
            SimpleNamespace(
                symbol=symbol,
                trend="BULLISH" if signal == "BUY" else "BEARISH",
                signal=signal,
                confidence=85.0,
            )
            for signal in signals[:cycles]
        ]


class FakeIntelligenceFlow:
    def __init__(self):
        self.actions = ["BUY", "WAIT", "WAIT", "SELL", "WAIT"]
        self.index = 0

    def create_report(self, consensus):
        action = self.actions[self.index]
        self.index += 1

        decision = SimpleNamespace(
            action=action,
            signal=action,
            confidence=85.0,
        )

        return SimpleNamespace(
            decision=decision,
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


def test_long_running_operational_loop_completes_trade_and_learning():
    intelligence_flow = FakeIntelligenceFlow()

    intelligence_runtime = OperationalIntelligenceRuntime(
        market_context_runtime=FakeMarketContextRuntime(),
        intelligence_flow=intelligence_flow,
    )

    intelligence_results = intelligence_runtime.run(
        symbol="BTCUSDT",
        cycles=5,
    )

    assert len(intelligence_results) == 5

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
            [65000.0, 65200.0, 65400.0, 66000.0, 66200.0],
        )
    ]

    paper_results = paper_runtime.run(
        cycle_inputs,
        symbol="BTCUSDT",
    )

    assert len(paper_results) == 5

    assert [result["action"] for result in paper_results] == [
        "OPEN",
        "HOLD",
        "HOLD",
        "CLOSE",
        "HOLD",
    ]

    close_result = paper_results[3]

    assert close_result["realized_pnl"] > 0
    assert close_result["learning_result"] == {"status": "LEARNED"}

    assert session.get_position() is None
    assert session.get_trade_count() == 1
    assert session.get_total_pnl() > 0

    assert len(outcome_bridge.calls) == 1

    learning_call = outcome_bridge.calls[0]

    assert learning_call["decision"] is intelligence_results[0]["decision"]
    assert learning_call["entry_price"] == 65000.0
    assert learning_call["exit_price"] == 66000.0
