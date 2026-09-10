from execution.paper_position import PaperPosition


class PaperPositionManager:

    def __init__(self):
        self.position = None

    def open_position(
        self,
        execution_result
    ):

        if self.position is not None:
            return None

        if execution_result.status != "EXECUTED":
            return None

        if execution_result.action not in ("BUY", "SELL"):
            return None

        if (
            not execution_result.symbol       
            or execution_result.quantity is None
            or execution_result.quantity <= 0
            or execution_result.price is None
            or execution_result.price <= 0
        ):
           return None

        self.position = PaperPosition(
            symbol=execution_result.symbol,
            side=execution_result.action,
            entry_price=execution_result.price,
            quantity=execution_result.quantity
        )

        return self.position

    def get_position(self):
        return self.position

    def calculate_pnl(self, current_price):
        if self.position is None:
            return 0.0

        return self.position.unrealized_pnl(
            current_price
        )

    def close_position(self):
        position = self.position
        self.position = None
        return position

    def close_position_with_pnl(self, current_price):
        if self.position is None:
            return None

        position = self.position

        realized_pnl = position.unrealized_pnl(
            current_price
        )

        self.position = None

        return {
            "position": position,
            "exit_price": current_price,
            "realized_pnl": realized_pnl
        }