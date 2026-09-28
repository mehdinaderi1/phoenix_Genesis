from execution.xt_futures_order_detail_request import XTFuturesOrderDetailRequest


class XTFuturesOrderDetailQueryBuilder:
    """
    Builds the verified XT Futures order-detail query.

    XT endpoint:
        GET /future/trade/v1/order/detail
    """

    ENDPOINT = "/future/trade/v1/order/detail"

    def build(self, order_id):
        return XTFuturesOrderDetailRequest(
            order_id=order_id
        )
