from execution.http_client import (
    HttpClient,
    HttpResponse
)
from execution.xt_futures_transport_request import (
    XTFuturesTransportRequest
)


class XTFuturesTransport:
    """
    Sends an authenticated XT Futures transport request
    through an injected HTTP client.

    The transport itself does not create signatures,
    build payloads, or interpret exchange responses.
    """

    def __init__(
        self,
        http_client: HttpClient,
        timeout=10
    ):
        self.http_client = http_client
        self.timeout = timeout

    def send(
        self,
        request: XTFuturesTransportRequest
    ) -> HttpResponse:
        if not isinstance(
            request,
            XTFuturesTransportRequest
        ):
            raise TypeError(
                "request must be XTFuturesTransportRequest"
            )

        return self.http_client.post(
            endpoint=request.endpoint,
            headers=request.headers(),
            body=request.body,
            timeout=self.timeout
        )
