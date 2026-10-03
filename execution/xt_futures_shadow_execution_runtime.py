from execution.paper_position_sizer import PaperPositionSizer
from execution.xt_futures_execution_orchestrator import XTFuturesExecutionOrchestrator


class XTFuturesShadowExecutionRuntime:
    """Prepares and optionally executes XT Futures shadow requests."""

    def __init__(
        self,
        balance,
        position_size_percent,
        orchestrator=None,
        position_sizer=None,
        transport=None,
        request_builder=None,
        timestamp=None,
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
        self.transport = transport
        self.request_builder = request_builder
        self.timestamp = timestamp

    def _get_current_position(self):
        """
        Resolve the currently held position for shadow execution.

        The existing close bridge owns the PaperTradingSession
        lifecycle, so its session is the authoritative source
        for the current position when a close bridge is configured.
        """
        position_close_bridge = getattr(
            self.orchestrator,
            "position_close_bridge",
            None,
        )

        if position_close_bridge is None:
            return None

        session = getattr(
            position_close_bridge,
            "session",
            None,
        )

        if session is None:
            return None

        get_position = getattr(
            session,
            "get_position",
            None,
        )

        if get_position is None:
            return None

        return get_position()

    def run(self, cycles, symbol="BTCUSDT"):
        results = []

        for cycle in cycles:
            proposal = cycle["action_proposal"]
            price = cycle["price"]

            position = self._get_current_position()

            if position is not None:
                quantity = position.quantity
            else:
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
                position=position,
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

            execution = None

            if (
                self.transport is not None
                and self.request_builder is not None
            ):
                transport_request = self.request_builder.build(
                    request=prepared["request"],
                    timestamp=self.timestamp,
                )

                transport_callable = lambda: self.transport.send(
                    transport_request
                )

                if (
                    self.orchestrator.reconciliation_service is not None
                    and self.orchestrator.reconciliation_service.detail_client is not None
                ):
                    execution = (
                        self.orchestrator.execute_and_reconcile(
                            action_proposal=proposal,
                            transport=transport_callable,
                            position=position,
                            quantity=quantity,
                            order_type="MARKET",
                        )
                    )
                else:
                    execution = self.orchestrator.execute(
                        action_proposal=proposal,
                        transport=transport_callable,
                        position=position,
                        quantity=quantity,
                        order_type="MARKET",
                    )

            results.append({
                "status": (
                    "EXECUTED"
                    if execution is not None
                    else "PREPARED"
                ),
                "prepared": prepared,
                "request": prepared["request"],
                "payload": prepared["payload"],
                "idempotency_key": prepared["idempotency_key"],
                "execution": execution,
            })

        return results
