from execution.paper_position_sizer import PaperPositionSizer
from execution.xt_futures_execution_orchestrator import (
    XTFuturesExecutionOrchestrator,
)


class XTFuturesPreparedExecutionRuntime:
    """
    Builds prepared XT Futures execution requests without
    sending network requests or executing real orders.
    """

    def __init__(
        self,
        balance,
        position_size_percent,
        orchestrator=None,
        position_sizer=None,
    ):
        self.balance = balance
        self.position_size_percent = position_size_percent
        self.orchestrator = (
            orchestrator
            or XTFuturesExecutionOrchestrator()
        )
        self.position_sizer = (
            position_sizer
            or PaperPositionSizer()
        )

    def run(self, cycles, symbol="BTCUSDT"):
        results = []

        for cycle in cycles:
            proposal = cycle["action_proposal"]
            price = cycle["price"]

            quantity = self.position_sizer.calculate_quantity(
                balance=self.balance,
                position_size_percent=(
                    self.position_size_percent
                ),
                entry_price=price,
            )

            if quantity <= 0:
                results.append({
                    "status": "NOT_PREPARED",
                    "prepared": None,
                    "execution": None,
                })
                continue

            if getattr(proposal, "symbol", None) is None:
                proposal.symbol = symbol

            prepared = self.orchestrator.prepare(
                action_proposal=proposal,
                quantity=quantity,
                order_type="MARKET",
            )

            if prepared is None:
                results.append({
                    "status": "NOT_PREPARED",
                    "prepared": None,
                    "execution": None,
                })
                continue

            results.append({
                "status": "PREPARED",
                "prepared": prepared,
                "request": prepared["request"],
                "payload": prepared["payload"],
                "idempotency_key": prepared[
                    "idempotency_key"
                ],
                "execution": None,
            })

        return results
