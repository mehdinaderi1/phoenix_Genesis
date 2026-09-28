from execution.http_client import HttpResponse
from execution.xt_futures_transport_request import (
    XTFuturesTransportRequest
)


class FakeHttpClient:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    def post(
        self,
        endpoint,
        headers,
        body,
        timeout=10
    ):
        self.calls.append({
            "endpoint": endpoint,
            "headers": headers,
            "body": body,
            "timeout": timeout,
        })

        if self.error is not None:
            raise self.error

        return self.response


def test_fake_http_client_captures_post():
    client = FakeHttpClient(
        response=HttpResponse(
            status_code=200,
            body='{"rc":0}'
        )
    )

    request = XTFuturesTransportRequest(
        endpoint="/future/trade/v1/order/create",
        body='{"symbol":"BTCUSDT"}',
        timestamp="1234567890",
        appkey="APPKEY",
        signature="SIGNATURE",
    )

    response = client.post(
        endpoint=request.endpoint,
        headers=request.headers(),
        body=request.body,
        timeout=10
    )

    assert response.status_code == 200
    assert response.body == '{"rc":0}'

    assert len(client.calls) == 1
    assert client.calls[0]["endpoint"] == (
        "/future/trade/v1/order/create"
    )
