from execution.xt_futures_order_detail_query import (
    XTFuturesOrderDetailQueryBuilder,
)
from execution.xt_futures_order_confirmation_interpreter import (
    XTFuturesOrderConfirmationInterpreter,
)
from execution.xt_futures_reconciler import XTFuturesReconciler


class XTFuturesOrderReconciliationService:
    def __init__(
        self,
        detail_client,
        query_builder=None,
        interpreter=None,
        reconciler=None,
    ):
        self.detail_client = detail_client
        self.query_builder = (
            query_builder or XTFuturesOrderDetailQueryBuilder()
        )
        self.interpreter = (
            interpreter
            or XTFuturesOrderConfirmationInterpreter()
        )
        self.reconciler = reconciler or XTFuturesReconciler()

    def _fetch_confirmation(self, order_id):
        if self.detail_client is None:
            raise ValueError("detail_client is required")

        request = self.query_builder.build(order_id)
        response = self.detail_client.fetch(request.order_id)

        return self.interpreter.interpret(response)

    def reconcile(self, idempotency_key, order_id):
        if not idempotency_key:
            raise ValueError("idempotency_key is required")

        if order_id is None:
            raise ValueError("order_id is required")

        confirmation = self._fetch_confirmation(order_id)

        return self.reconciler.reconcile(
            idempotency_key=idempotency_key,
            confirmation=confirmation,
        )

    def reconcile_with_confirmation(
        self,
        idempotency_key,
        order_id,
    ):
        if not idempotency_key:
            raise ValueError("idempotency_key is required")

        if order_id is None:
            raise ValueError("order_id is required")

        confirmation = self._fetch_confirmation(order_id)

        result = self.reconciler.reconcile(
            idempotency_key=idempotency_key,
            confirmation=confirmation,
        )

        return {
            "result": result,
            "confirmation": confirmation,
        }
