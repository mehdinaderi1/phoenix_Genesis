from types import SimpleNamespace

from execution.operational_loop import OperationalLoop


class FaultyCycle:
    def __init__(self):
        self.calls = 0

    def process(self, action_proposal, price, symbol="BTCUSDT", decision=None):
        self.calls += 1

        if self.calls == 3:
            raise RuntimeError("simulated operational cycle failure")

        return {
            "action": "HOLD",
            "price": price,
        }


def test_operational_loop_continues_after_single_cycle_failure():
    cycle = FaultyCycle()
    loop = OperationalLoop(cycle)

    inputs = [
        {
            "action_proposal": SimpleNamespace(action="WAIT"),
            "price": price,
            "symbol": "BTCUSDT",
            "decision": SimpleNamespace(action="WAIT"),
        }
        for price in [65000.0, 65100.0, 65200.0, 65300.0, 65400.0]
    ]

    results = loop.run(inputs)

    assert len(results) == 5

    assert [result.status for result in results] == [
        "SUCCESS",
        "SUCCESS",
        "ERROR",
        "SUCCESS",
        "SUCCESS",
    ]

    assert results[2].error == (
        "simulated operational cycle failure"
    )

    assert cycle.calls == 5
