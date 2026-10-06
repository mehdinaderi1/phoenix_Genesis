from execution.xt_futures_attempt_state import (
    XTFuturesAttemptState,
)
from execution.xt_futures_execution_idempotency_guard import (
    XTFuturesExecutionIdempotencyGuard,
    XTFuturesIdempotencyState,
)
from execution.xt_futures_execution_result_bridge import (
    XTFuturesExecutionResultBridge,
)
from execution.xt_futures_idempotency import (
    XTFuturesIdempotencyKeyBuilder,
)
from execution.xt_futures_order_mapper import (
    XTFuturesOrderMapper,
)
from execution.xt_futures_order_payload import (
    XTFuturesOrderPayloadBuilder,
)
from execution.xt_futures_order_reconciliation_service import (
    XTFuturesOrderReconciliationService,
)
from execution.xt_futures_position_bridge import (
    XTFuturesPositionBridge,
)
from execution.xt_futures_position_close_bridge import (
    XTFuturesPositionCloseBridge,
)
from execution.xt_futures_retry_executor import (
    XTFuturesRetryExecutor,
)


class XTFuturesExecutionOrchestrator:
    """
    Coordinates the Phoenix -> XT Futures execution contracts.

    This layer does not send real HTTP requests directly.
    Transport is injected into the retry executor.

    Confirmation is performed only by the explicit
    execute_and_reconcile() lifecycle.

    A confirmed execution is bridged into the appropriate
    Phoenix position lifecycle:
    - OPEN -> XTFuturesPositionBridge
    - CLOSE -> XTFuturesPositionCloseBridge
    """

    def __init__(
        self,
        order_mapper=None,
        payload_builder=None,
        idempotency_builder=None,
        idempotency_guard=None,
        retry_executor=None,
        reconciliation_service=None,
        execution_result_bridge=None,
        position_bridge=None,
        position_close_bridge=None,
    ):
        self.order_mapper = (
            order_mapper or XTFuturesOrderMapper()
        )
        self.payload_builder = (
            payload_builder or XTFuturesOrderPayloadBuilder()
        )
        self.idempotency_builder = (
            idempotency_builder
            or XTFuturesIdempotencyKeyBuilder()
        )
        self.idempotency_guard = (
            idempotency_guard
            or XTFuturesExecutionIdempotencyGuard()
        )
        self.retry_executor = (
            retry_executor or XTFuturesRetryExecutor()
        )
        self.reconciliation_service = (
            reconciliation_service
            or XTFuturesOrderReconciliationService(
                detail_client=None
            )
        )
        self.execution_result_bridge = (
            execution_result_bridge
            or XTFuturesExecutionResultBridge()
        )
        self.position_bridge = (
            position_bridge or XTFuturesPositionBridge()
        )
        self.position_close_bridge = position_close_bridge

    def prepare(
        self,
        action_proposal,
        position=None,
        quantity=None,
        order_type="MARKET",
        price=None,
        attempt_identity=None,
    ):
        if getattr(action_proposal, "status", None) != "APPROVED":
            return None

        effective_quantity = quantity

        if position is not None:
            effective_quantity = position.quantity

        request = self.order_mapper.build(
            action_proposal=action_proposal,
            position=position,
            quantity=effective_quantity,
            order_type=order_type,
            price=price,
        )

        if request is None:
            return None

        payload = self.payload_builder.build(request)

        idempotency_key = self.idempotency_builder.build(
            symbol=request.symbol,
            order_side=request.order_side,
            position_side=request.position_side,
            order_type=request.order_type,
            quantity=request.quantity,
            price=request.price,
            attempt_identity=attempt_identity,
        )

        return {
            "request": request,
            "payload": payload,
            "idempotency_key": idempotency_key,
        }

    def execute(
        self,
        action_proposal,
        transport,
        position=None,
        quantity=None,
        order_type="MARKET",
        price=None,
        max_attempts=3,
        attempt_identity=None,
    ):
        prepared = self.prepare(
            action_proposal=action_proposal,
            position=position,
            quantity=quantity,
            order_type=order_type,
            price=price,
            attempt_identity=attempt_identity,
        )

        if prepared is None:
            return None

        idempotency_key = prepared["idempotency_key"].value

        if not self.idempotency_guard.can_submit(
            idempotency_key
        ):
            state = self.idempotency_guard.get_state(
                idempotency_key
            )
            raise PermissionError(
                "Duplicate execution is blocked for idempotency key "
                f"{idempotency_key} (state={state.value})"
            )

        self.idempotency_guard.register(
            idempotency_key,
            XTFuturesIdempotencyState.SUBMITTED,
        )

        result = self.retry_executor.execute(
            transport=transport,
            idempotency_key=idempotency_key,
            max_attempts=max_attempts,
        )

        if result["state"] == XTFuturesAttemptState.REJECTED:
            self.idempotency_guard.update(
                idempotency_key,
                XTFuturesIdempotencyState.REJECTED,
            )
        elif result["state"] == XTFuturesAttemptState.UNKNOWN:
            self.idempotency_guard.update(
                idempotency_key,
                XTFuturesIdempotencyState.UNKNOWN,
            )

        response = result.get("response")
        order_id = None

        if response is not None and isinstance(
            response.body,
            dict,
        ):
            response_result = response.body.get("result")

            if isinstance(response_result, dict):
                order_id = response_result.get("orderId")

        result["order_id"] = order_id

        return {
            "request": prepared["request"],
            "payload": prepared["payload"],
            "idempotency_key": prepared["idempotency_key"],
            "execution": result,
        }

    def execute_and_reconcile(
        self,
        action_proposal,
        transport,
        position=None,
        quantity=None,
        order_type="MARKET",
        price=None,
        max_attempts=3,
        attempt_identity=None,
    ):
        result = self.execute(
            action_proposal=action_proposal,
            transport=transport,
            position=position,
            quantity=quantity,
            order_type=order_type,
            price=price,
            max_attempts=max_attempts,
            attempt_identity=attempt_identity,
        )

        if result is None:
            return None

        execution = result["execution"]
        order_id = execution.get("order_id")

        result["reconciliation"] = None
        result["execution_result"] = None
        result["position"] = None
        result["close"] = None

        if (
            execution.get("state")
            != XTFuturesAttemptState.SENT
            or order_id is None
        ):
            return result

        numeric_order_id = int(order_id)

        reconciliation = (
            self.reconciliation_service
            .reconcile_with_confirmation(
                idempotency_key=(
                    result["idempotency_key"].value
                ),
                order_id=numeric_order_id,
            )
        )

        result["reconciliation"] = reconciliation["result"]

        reconciliation_result = result["reconciliation"]

        if isinstance(
            reconciliation_result,
            XTFuturesAttemptState,
        ):
            reconciliation_state = reconciliation_result
        else:
            reconciliation_state = reconciliation_result.state

        if reconciliation_state == XTFuturesAttemptState.CONFIRMED:
            self.idempotency_guard.update(
                result["idempotency_key"].value,
                XTFuturesIdempotencyState.CONFIRMED,
            )
        elif reconciliation_state == XTFuturesAttemptState.REJECTED:
            self.idempotency_guard.update(
                result["idempotency_key"].value,
                XTFuturesIdempotencyState.REJECTED,
            )
        elif reconciliation_state == XTFuturesAttemptState.UNKNOWN:
            self.idempotency_guard.update(
                result["idempotency_key"].value,
                XTFuturesIdempotencyState.UNKNOWN,
            )

        confirmation = reconciliation["confirmation"]

        result["execution_result"] = (
            self.execution_result_bridge.build(
                confirmation=confirmation,
                action=result["request"].order_side,
                symbol=result["request"].symbol,
            )
        )

        if result["execution_result"] is None:
            return result

        if result["execution_result"].status == "EXECUTED":
            self.idempotency_guard.update(
                result["idempotency_key"].value,
                XTFuturesIdempotencyState.CONFIRMED,
            )

        if (
            position is not None
            and self.position_close_bridge is not None
        ):
            result["close"] = (
                self.position_close_bridge.apply(
                    result["execution_result"]
                )
            )
            return result

        result["position"] = self.position_bridge.apply(
            result["execution_result"]
        )

        return result