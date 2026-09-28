from execution.xt_futures_attempt_state import XTFuturesAttemptState
from execution.xt_futures_order_reconciliation_service import (
    XTFuturesOrderReconciliationService,
)
from execution.xt_futures_response import XTFuturesResponse


class FakeDetailClient:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def fetch(self, order_id):
        self.calls.append(order_id)
        return self.response


def make_response(state="FILLED", order_id="123"):
    return XTFuturesResponse(
        status_code=200,
        ok=True,
        body={
            "result": {
                "orderId": order_id,
                "state": state,
            }
        },
        raw_body="{}",
    )


def test_reconciliation_service_confirms_filled_order():
    client = FakeDetailClient(make_response("FILLED"))

    service = XTFuturesOrderReconciliationService(
        detail_client=client
    )

    result = service.reconcile(
        idempotency_key="idem-123",
        order_id=123,
    )

    assert result.state == XTFuturesAttemptState.CONFIRMED
    assert result.idempotency_key == "idem-123"
    assert client.calls == [123]


def test_reconciliation_service_rejects_canceled_order():
    client = FakeDetailClient(make_response("CANCELED"))

    service = XTFuturesOrderReconciliationService(
        detail_client=client
    )

    result = service.reconcile(
        idempotency_key="idem-123",
        order_id=123,
    )

    assert result.state == XTFuturesAttemptState.REJECTED
    assert result.error == "Order state: CANCELED"


def test_reconciliation_service_preserves_unknown():
    client = FakeDetailClient(make_response("NEW"))

    service = XTFuturesOrderReconciliationService(
        detail_client=client
    )

    result = service.reconcile(
        idempotency_key="idem-123",
        order_id=123,
    )

    assert result.state == XTFuturesAttemptState.UNKNOWN
    assert result.error == "Order state: NEW"


def test_reconciliation_service_requires_order_id():
    client = FakeDetailClient(make_response())

    service = XTFuturesOrderReconciliationService(
        detail_client=client
    )

    try:
        service.reconcile(
            idempotency_key="idem-123",
            order_id=None,
        )
        assert False
    except ValueError:
        pass


def test_reconciliation_service_queries_detail_once():
    client = FakeDetailClient(make_response("NEW"))

    service = XTFuturesOrderReconciliationService(
        detail_client=client
    )

    service.reconcile(
        idempotency_key="idem-123",
        order_id=123,
    )

    assert client.calls == [123]
