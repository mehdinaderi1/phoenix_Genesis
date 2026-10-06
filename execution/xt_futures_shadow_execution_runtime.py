from execution.paper_position_sizer import PaperPositionSizer
from execution.xt_futures_execution_orchestrator import (
    XTFuturesExecutionOrchestrator,
)
from execution.xt_futures_attempt_state import (
    XTFuturesAttemptState,
)


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

        # Recovery identity is scoped to this runtime session.
        #
        # logical_order_identity -> current recovery attempt number
        self._recovery_attempts = {}

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

    @staticmethod
    def _logical_order_identity(request):
        """
        Build a stable identity for the logical order.

        Recovery attempt identity is deliberately excluded.
        """
        return (
            request.symbol,
            request.order_side,
            request.position_side,
            request.order_type,
            request.quantity,
            request.price,
        )

    @staticmethod
    def _execution_state(result):
        """
        Resolve the final state relevant to cross-cycle recovery.

        Reconciliation is authoritative when it exists because an
        order can be SENT successfully while later reconciliation
        determines that the exchange rejected or could not confirm it.

        If reconciliation has not occurred, fall back to the
        transport/execution attempt state.
        """
        if not isinstance(result, dict):
            return None

        reconciliation = result.get("reconciliation")

        if reconciliation is not None:
            reconciliation_result = reconciliation

            if isinstance(reconciliation, dict):
                reconciliation_result = reconciliation.get(
                    "result"
                )

            if isinstance(
                reconciliation_result,
                XTFuturesAttemptState,
            ):
                return reconciliation_result

            reconciliation_state = getattr(
                reconciliation_result,
                "state",
                None,
            )

            if reconciliation_state is not None:
                return reconciliation_state

        execution = result.get("execution")

        if not isinstance(execution, dict):
            return None

        return execution.get("state")

    def _attempt_identity(self, logical_order_identity):
        return self._recovery_attempts.get(
            logical_order_identity,
            0,
        )

    def _record_recovery_state(
        self,
        logical_order_identity,
        execution_result,
    ):
        """
        Advance the recovery attempt after a rejected or unknown
        logical execution result.

        Retries inside the same execution attempt continue to use
        the same idempotency key because retry ownership remains
        inside XTFuturesRetryExecutor.
        """
        state = self._execution_state(
            execution_result
        )

        if state in (
            XTFuturesAttemptState.REJECTED,
            XTFuturesAttemptState.UNKNOWN,
            "REJECTED",
            "UNKNOWN",
        ):
            current_attempt = self._recovery_attempts.get(
                logical_order_identity,
                0,
            )

            self._recovery_attempts[
                logical_order_identity
            ] = current_attempt + 1

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

            # First build the logical request so the runtime can
            # derive a stable identity independent of recovery
            # attempt number.
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

            logical_order_identity = (
                self._logical_order_identity(
                    prepared["request"]
                )
            )

            attempt_identity = self._attempt_identity(
                logical_order_identity
            )

            # Rebuild the prepared request with the current
            # execution-attempt identity so a new recovery attempt
            # receives a new idempotency key.
            prepared = self.orchestrator.prepare(
                action_proposal=proposal,
                position=position,
                quantity=quantity,
                order_type="MARKET",
                attempt_identity=attempt_identity,
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
                    self.orchestrator.reconciliation_service
                    is not None
                    and (
                        self.orchestrator
                        .reconciliation_service
                        .detail_client
                        is not None
                    )
                ):
                    execution = (
                        self.orchestrator.execute_and_reconcile(
                            action_proposal=proposal,
                            transport=transport_callable,
                            position=position,
                            quantity=quantity,
                            order_type="MARKET",
                            attempt_identity=attempt_identity,
                        )
                    )
                else:
                    execution = self.orchestrator.execute(
                        action_proposal=proposal,
                        transport=transport_callable,
                        position=position,
                        quantity=quantity,
                        order_type="MARKET",
                        attempt_identity=attempt_identity,
                    )

            self._record_recovery_state(
                logical_order_identity,
                execution,
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