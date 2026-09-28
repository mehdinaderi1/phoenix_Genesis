from execution.xt_futures_order_request import XTFuturesOrderRequest


class XTFuturesOrderPayloadBuilder:
    """
    Converts a validated Phoenix XT order request
    into the XT Futures API payload.

    This builder does not send network requests.
    """

    def build(self, request: XTFuturesOrderRequest):
        if not isinstance(
            request,
            XTFuturesOrderRequest
        ):
            raise TypeError(
                "request must be XTFuturesOrderRequest"
            )

        payload = {
            "symbol": request.symbol,
            "orderSide": request.order_side,
            "positionSide": request.position_side,
            "orderType": request.order_type,
            "origQty": request.quantity,
        }

        if request.price is not None:
            payload["price"] = request.price

        return payload
