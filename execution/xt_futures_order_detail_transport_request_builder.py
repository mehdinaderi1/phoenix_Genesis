from execution.xt_futures_order_detail_query import XTFuturesOrderDetailQueryBuilder
from exchanges.xt_futures_private_adapter import XTFuturesPrivateAdapter
from execution.xt_futures_transport_request import XTFuturesTransportRequest


class XTFuturesOrderDetailTransportRequestBuilder:
    """Builds an authenticated XT Futures order-detail GET request."""

    BASE_URL = "https://fapi.xt.com"

    def __init__(self, appkey, secret_key, timestamp=None):
        self.appkey = appkey
        self.secret_key = secret_key
        self.timestamp = timestamp
        self.query_builder = XTFuturesOrderDetailQueryBuilder()
        self.adapter = XTFuturesPrivateAdapter(
            appkey=appkey,
            secret_key=secret_key,
        )

    def build(self, order_id, timestamp=None):
        effective_timestamp = (
            self.timestamp
            if timestamp is None
            else timestamp
        )

        if effective_timestamp is None or effective_timestamp == "":
            raise ValueError("timestamp is required")

        request = self.query_builder.build(order_id)
        query_string = self.adapter.build_query_string(
            request.to_query_params()
        )

        signature = self.adapter.generate_signature(
            timestamp=str(effective_timestamp),
            endpoint=self.query_builder.ENDPOINT,
            query_string=query_string,
        )

        return XTFuturesTransportRequest(
            endpoint=(
                f"{self.BASE_URL}"
                f"{self.query_builder.ENDPOINT}"
                f"?{query_string}"
            ),
            body="",
            timestamp=str(effective_timestamp),
            appkey=self.appkey,
            signature=signature,
        )
