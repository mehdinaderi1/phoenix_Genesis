import json

from execution.http_client import HttpResponse
from execution.xt_futures_order_detail_client import XTFuturesOrderDetailClient
from execution.xt_futures_order_detail_transport import XTFuturesOrderDetailTransport
from execution.xt_futures_order_detail_transport_request_builder import (
    XTFuturesOrderDetailTransportRequestBuilder,
)
from execution.xt_futures_order_reconciliation_service import (
    XTFuturesOrderReconciliationService,
)
from execution.xt_futures_attempt_state import XTFuturesAttemptState


class FakeHttpClient:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def get(self, endpoint, headers, timeout=10):
        self.calls.append({
            "endpoint": endpoint,
            "headers": headers,
            "timeout": timeout,
        })
        return self.response


def test_real_order_detail_composition_reconciles_filled_order():
    response = HttpResponse(
        status_code=200,
        body=json.dumps({
            "rc": 0,
            "result": {
                "orderId": 1234567890,
                "state": "FILLED",
                "executedQty": "0.001",
                "avgPrice": "50000",
            },
        }),
    )

    http_client = FakeHttpClient(response)

    request_builder = XTFuturesOrderDetailTransportRequestBuilder(
        appkey="APPKEY",
        secret_key="SECRET",
        timestamp="1700000000000",
    )

    transport = XTFuturesOrderDetailTransport(
        http_client=http_client,
        timeout=15,
    )

    detail_client = XTFuturesOrderDetailClient(
        transport=transport,
        request_builder=request_builder,
    )

    service = XTFuturesOrderReconciliationService(
        detail_client=detail_client,
    )

    result = service.reconcile(
        idempotency_key="idem-123",
        order_id=1234567890,
    )

    assert result.state == XTFuturesAttemptState.CONFIRMED
    assert result.idempotency_key == "idem-123"

    assert len(http_client.calls) == 1
    call = http_client.calls[0]

    assert call["endpoint"] == (
        "https://fapi.xt.com"
        "/future/trade/v1/order/detail?"
        "orderId=1234567890"
    )
    assert call["timeout"] == 15
    assert call["headers"]["validate-appkey"] == "APPKEY"
    assert call["headers"]["validate-timestamp"] == "1700000000000"
    assert len(call["headers"]["validate-signature"]) == 64
