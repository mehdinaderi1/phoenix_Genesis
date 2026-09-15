from types import SimpleNamespace

from execution.paper_trading_session import PaperTradingSession


class FaultyCycle:
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


class FaultTolerantOperationalLoop:
    def __init__(self, cycle):
        self.cycle = cycle

    def run(self, inputs):
        results = []

        for cycle_input in inputs:
            try:
                result = self.cycle.process(
                    action_proposal=cycle_input["action_proposal"],
                    price=cycle_input["price"],
                    symbol=cycle_input.get("symbol", "BTCUSDT"),
                    decision=cycle_input.get("decision"),
                )
            except Exception as exc:
                results.append(
                    {
                        "status": "ERROR",
                        "error": str(exc),
                    }
                )
                continue

            results.append(
                {
                    "status": "SUCCESS",
                    "result": result,
                }
            )

        return results


def test_operational_loop_continues_after_single_cycle_failure():
    session = PaperTradingSession(initial_balance=1000.0)

    cycle = FaultyCycle()
    loop = FaultTolerantOperationalLoop(cycle)

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

    assert [result["status"] for result in results] == [
        "SUCCESS",
        "SUCCESS",
        "ERROR",
        "SUCCESS",
        "SUCCESS",
    ]

    assert results[2]["error"] == (
        "simulated operational cycle failure"
    )

    assert cycle.calls == 5
