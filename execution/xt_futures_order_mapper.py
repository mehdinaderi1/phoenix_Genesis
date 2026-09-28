from execution.xt_futures_order_request import XTFuturesOrderRequest


class XTFuturesOrderMapper:
    """
    Maps Phoenix action + current position state
    to an XT USDT-M Futures order request.

    This mapper does not execute orders and does not
    mutate the action proposal or position.
    """

    def build(
        self,
        action_proposal,
        position=None,
        quantity=None,
        order_type="MARKET",
        price=None
    ):
        action = getattr(action_proposal, "action", None)
        symbol = getattr(action_proposal, "symbol", None)

        if action not in ("BUY", "SELL"):
            return None

        if not symbol:
            raise ValueError("symbol is required")

        if quantity is None:
            raise ValueError("quantity is required")

        if position is None:
            position_side = (
                "LONG"
                if action == "BUY"
                else "SHORT"
            )

        else:
            current_side = getattr(
                position,
                "side",
                None
            )

            if current_side not in ("BUY", "SELL"):
                raise ValueError(
                    "position.side must be BUY or SELL"
                )

            if action == current_side:
                return None

            position_side = (
                "LONG"
                if current_side == "BUY"
                else "SHORT"
            )

        return XTFuturesOrderRequest(
            symbol=symbol,
            order_side=action,
            position_side=position_side,
            order_type=order_type,
            quantity=quantity,
            price=price
        )
