from execution.http_client import HttpClient
from execution.xt_futures_response_normalizer import XTFuturesResponseNormalizer
from execution.xt_futures_transport_request import XTFuturesTransportRequest


class XTFuturesOrderDetailTransport:
    """HTTP GET transport for XT Futures order detail."""

    def __init__(
        self,
        http_client: HttpClient,
        timeout=10,
        response_normalizer=None,
    ):
        self.http_client = http_client
        self.timeout = timeout
        self.response_normalizer = (
            response_normalizer or XTFuturesResponseNormalizer()
        )

    def send(self, request: XTFuturesTransportRequest):
        if not isinstance(request, XTFuturesTransportRequest):
            raise TypeError("request must be XTFuturesTransportRequest")

        response = self.http_client.get(
            endpoint=request.endpoint,
            headers=request.headers(),
            timeout=self.timeout,
        )

        return self.response_normalizer.normalize(response)

    def fetch(self, order_id, request_builder):
        request = request_builder.build(order_id)
        return self.send(request)
