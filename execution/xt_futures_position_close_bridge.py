from execution.execution_result import ExecutionResult
from execution.paper_trading_session import PaperTradingSession


class XTFuturesPositionCloseBridge:
    """
    Bridges a confirmed XT close execution into the
    existing Phoenix PaperTradingSession close lifecycle.

    This bridge does not create a new position.
    It reuses the existing session close contract so
    realized PnL, trade history, portfolio and learning
    remain owned by PaperTradingSession.
    """

    def __init__(self, session):
        if not isinstance(session, PaperTradingSession):
            raise TypeError("session must be PaperTradingSession")

        self.session = session

    def apply(self, execution_result):
        if not isinstance(execution_result, ExecutionResult):
            raise TypeError("execution_result must be ExecutionResult")

        if execution_result.status != "EXECUTED":
            return None

        if execution_result.action not in ("BUY", "SELL"):
            return None

        if not execution_result.symbol:
            return None

        if execution_result.price is None or execution_result.price <= 0:
            return None

        position = self.session.get_position()

        if position is None:
            return None

        if position.symbol != execution_result.symbol:
            return None

        # A close execution must be opposite to the
        # currently held position.
        if execution_result.action == position.side:
            return None

        return self.session.close_position(
            exit_price=execution_result.price
        )
