from types import SimpleNamespace

from execution.paper_trading_runtime import PaperTradingRuntime
from execution.paper_trading_session import PaperTradingSession


class FaultTolerantCycle:
    def __init__(self):
        self.calls = 0

    def process(self, action_proposal, price, symbol="BTCUSDT", decision=None):
        self.calls += 1

        if self.calls == 3:
            raise RuntimeError("simulated operational cycle failure")

        return {
            "action": "HOLD",
            "execution_result": None,
            "position": None,
            "exit_price": None,
            "realized_pnl": 0.0,
            "trade": None,
            "learning_result": None,
        }


def test_operational_loop_failure_is_visible_to_caller():
    session = PaperTradingSession(initial_balance=1000.0)
    cycle = FaultTolerantCycle()
    runtime = PaperTradingRuntime(session=session, cycle=cycle)

    inputs = [
        {
            "action_proposal": SimpleNamespace(action="WAIT"),
            "price": price,
            "symbol": "BTCUSDT",
            "decision": SimpleNamespace(action="WAIT"),
        }
        for price in [65000.0, 65100.0, 65200.0, 65300.0]
    ]

    try:
        runtime.run(inputs, symbol="BTCUSDT")
    except RuntimeError as exc:
        assert str(exc) == "simulated operational cycle failure"
    else:
        raise AssertionError("Expected operational cycle failure")

    assert cycle.calls == 3
