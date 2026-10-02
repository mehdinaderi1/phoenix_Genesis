from execution.paper_position_sizer import PaperPositionSizer
from execution.xt_futures_execution_orchestrator import XTFuturesExecutionOrchestrator
from execution.xt_futures_real_execution_gate import XTFuturesRealExecutionGate


class XTFuturesRealExecutionRuntime:
    """Controlled boundary for authorized XT Futures real execution."""

    def __init__(
        self,
        balance,
        position_size_percent,
        gate,
        orchestrator=None,
        position_sizer=None,
        request_builder=None,
        transport=None,
        timestamp=None,
    ):
        if not isinstance(gate, XTFuturesRealExecutionGate):
            raise TypeError(
                "gate must be XTFuturesRealExecutionGate"
            )

        if request_builder is None:
            raise ValueError("request_builder is required")

        if transport is None:
            raise ValueError("transport is required")

        self.balance = balance
        self.position_size_percent = position_size_percent
        self.gate = gate
        self.orchestrator = (
            orchestrator
            or XTFuturesExecutionOrchestrator()
        )
        self.position_sizer = (
            position_sizer
            or PaperPositionSizer()
        )
        self.request_builder = request_builder
        self.transport = transport
        self.timestamp = timestamp

    def run(self, cycles, symbol="BTCUSDT"):
        self.gate.authorize()

        results = []

        for cycle in cycles:
            proposal = cycle["action_proposal"]
            price = cycle["price"]

            quantity = self.position_sizer.calculate_quantity(
                balance=self.balance,
                position_size_percent=self.position_size_percent,
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

            transport_request = self.request_builder.build(
                request=prepared["request"],
                timestamp=self.timestamp,
            )

            execution = self.orchestrator.execute(
                action_proposal=proposal,
                transport=lambda: self.transport.send(
                    transport_request
                ),
                quantity=quantity,
                order_type="MARKET",
            )

            execution_status = execution["execution"]["state"]

            results.append({
                "status": execution_status,
                "prepared": prepared,
                "request": prepared["request"],
                "payload": prepared["payload"],
                "idempotency_key": prepared["idempotency_key"],
                "execution": execution,
            })

        return results
