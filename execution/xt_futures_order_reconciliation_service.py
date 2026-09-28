from execution.xt_futures_order_detail_query import (
    XTFuturesOrderDetailQueryBuilder,
)
from execution.xt_futures_order_confirmation_interpreter import (
    XTFuturesOrderConfirmationInterpreter,
)
from execution.xt_futures_reconciler import XTFuturesReconciler


class XTFuturesOrderReconciliationService:
    """
    Orchestrates XT Futures order-detail reconciliation.

    This service does not:
    - create orders
    - retry order creation
    - perform HTTP directly
    - mutate positions
    """

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
            interpreter or XTFuturesOrderConfirmationInterpreter()
        )
        self.reconciler = reconciler or XTFuturesReconciler()

    def reconcile(self, idempotency_key, order_id):
        if not idempotency_key:
            raise ValueError("idempotency_key is required")

        if order_id is None:
            raise ValueError("order_id is required")

        request = self.query_builder.build(order_id)

        confirmation = self.detail_client.fetch(
            request.order_id
        )

        interpreted = self.interpreter.interpret(
            confirmation
        )

        return self.reconciler.reconcile(
            idempotency_key=idempotency_key,
            confirmation=interpreted,
        )
