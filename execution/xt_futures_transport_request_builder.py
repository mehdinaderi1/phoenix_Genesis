"""Build authenticated XT Futures transport requests."""

import json

from exchanges.xt_futures_private_adapter import XTFuturesPrivateAdapter
from execution.xt_futures_order_request import XTFuturesOrderRequest
from execution.xt_futures_transport_request import XTFuturesTransportRequest


class XTFuturesTransportRequestBuilder:
    """Build an authenticated XT transport request from an order request."""

    def __init__(
        self,
        appkey,
        secret_key,
        endpoint="/future/trade/v1/order/create",
    ):
        self.endpoint = endpoint
        self.adapter = XTFuturesPrivateAdapter(
            appkey=appkey,
            secret_key=secret_key,
        )

    def build(self, request: XTFuturesOrderRequest, timestamp):
        if not isinstance(request, XTFuturesOrderRequest):
            raise TypeError(
                "request must be XTFuturesOrderRequest"
            )

        if timestamp is None or timestamp == "":
            raise ValueError("timestamp is required")

        body = json.dumps(
            request.to_dict(),
            separators=(",", ":"),
            sort_keys=True,
        )

        signature = self.adapter.generate_body_signature(
            timestamp=timestamp,
            endpoint=self.endpoint,
            request_body=body,
        )

        return XTFuturesTransportRequest(
            endpoint=self.endpoint,
            body=body,
            timestamp=str(timestamp),
            appkey=self.adapter.appkey,
            signature=signature,
        )
