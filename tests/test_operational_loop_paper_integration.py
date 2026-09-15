from types import SimpleNamespace

from execution.operational_loop import OperationalLoop
from execution.paper_trading_runtime import PaperTradingRuntime
from execution.paper_trading_session import PaperTradingSession


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


class FaultInjectingPaperCycle:
    def __init__(self, runtime):
        self.runtime = runtime
        self.calls = 0

    def process(self, action_proposal, price, symbol="BTCUSDT", decision=None):
        self.calls += 1

        if self.calls == 3:
            raise RuntimeError("simulated operational cycle failure")

        return self.runtime.cycle.process(
            action_proposal=action_proposal,
            price=price,
            symbol=symbol,
            decision=decision,
        )


def test_operational_loop_recovers_and_completes_paper_trade():
    outcome_bridge = RecordingOutcomeBridge()

    session = PaperTradingSession(
        initial_balance=1000.0,
        outcome_bridge=outcome_bridge,
    )

    paper_runtime = PaperTradingRuntime(session=session)

    cycle = FaultInjectingPaperCycle(paper_runtime)

    loop = OperationalLoop(cycle)

    buy_decision = SimpleNamespace(
        action="BUY",
        signal="BUY",
        confidence=85.0,
    )

    wait_decision = SimpleNamespace(
        action="WAIT",
        signal="WAIT",
        confidence=85.0,
    )

    sell_decision = SimpleNamespace(
        action="SELL",
        signal="SELL",
        confidence=85.0,
    )

    inputs = [
        {
            "action_proposal": SimpleNamespace(action="BUY"),
            "price": 65000.0,
            "symbol": "BTCUSDT",
            "decision": buy_decision,
        },
        {
            "action_proposal": SimpleNamespace(action="WAIT"),
            "price": 65500.0,
            "symbol": "BTCUSDT",
            "decision": wait_decision,
        },
        {
            "action_proposal": SimpleNamespace(action="WAIT"),
            "price": 66000.0,
            "symbol": "BTCUSDT",
            "decision": wait_decision,
        },
        {
            "action_proposal": SimpleNamespace(action="SELL"),
            "price": 67000.0,
            "symbol": "BTCUSDT",
            "decision": sell_decision,
        },
    ]

    results = loop.run(inputs)

    assert len(results) == 4

    assert [result.status for result in results] == [
        "SUCCESS",
        "SUCCESS",
        "ERROR",
        "SUCCESS",
    ]

    assert results[0].result["action"] == "OPEN"
    assert results[1].result["action"] == "HOLD"
    assert results[2].error == "simulated operational cycle failure"
    assert results[3].result["action"] == "CLOSE"

    assert results[3].result["realized_pnl"] > 0
    assert results[3].result["learning_result"] == {"status": "LEARNED"}

    assert session.get_position() is None
    assert session.get_trade_count() == 1
    assert session.get_total_pnl() > 0

    assert len(outcome_bridge.calls) == 1
    assert outcome_bridge.calls[0]["entry_price"] == 65000.0
    assert outcome_bridge.calls[0]["exit_price"] == 67000.0
