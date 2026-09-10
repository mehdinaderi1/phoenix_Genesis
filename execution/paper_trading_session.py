from execution.paper_execution_engine import PaperExecutionEngine
from execution.paper_position_manager import PaperPositionManager
from execution.paper_portfolio import PaperPortfolio
from execution.paper_trade_history import PaperTradeHistory


class PaperTradingSession:

    def __init__(
        self,
        initial_balance=1000.0,
        position_size_percent=1.0,
        execution_engine=None,
        position_manager=None,
        portfolio=None,
        trade_history=None
    ):
        self.position_size_percent = position_size_percent

        self.execution_engine = (
            execution_engine
            or PaperExecutionEngine()
        )

        self.position_manager = (
            position_manager
            or PaperPositionManager()
        )

        self.portfolio = (
            portfolio
            or PaperPortfolio.create(
                initial_balance=initial_balance
            )
        )

        self.trade_history = (
            trade_history
            or PaperTradeHistory()
        )

    def process_action(
        self,
        action_proposal,
        price,
        symbol="BTCUSDT"
    ):
        execution_result = (
            self.execution_engine.execute(
                action_proposal=action_proposal,
                price=price,
                symbol=symbol,
                balance=self.portfolio.get_balance(),
                position_size_percent=self.position_size_percent
            )
        )

        position = (
            self.position_manager.open_position(
                execution_result
            )
        )

        return {
            "execution_result": execution_result,
            "position": position,
            "portfolio": self.portfolio,
            "trade_history": self.trade_history
        }

    def close_position(self, exit_price):
        closed = (
            self.position_manager.close_position_with_pnl(
                current_price=exit_price
            )
        )

        if closed is None:
            return None

        realized_pnl = closed["realized_pnl"]

        self.portfolio.apply_realized_pnl(
            realized_pnl
        )

        trade = self.trade_history.add_trade(
            position=closed["position"],
            exit_price=closed["exit_price"],
            realized_pnl=realized_pnl
        )

        return {
            "position": closed["position"],
            "exit_price": closed["exit_price"],
            "realized_pnl": realized_pnl,
            "trade": trade,
            "portfolio": self.portfolio,
            "trade_history": self.trade_history
        }

    def get_position(self):
        return self.position_manager.get_position()

    def get_balance(self):
        return self.portfolio.get_balance()

    def get_total_pnl(self):
        return self.portfolio.get_total_pnl()

    def get_trade_count(self):
        return self.trade_history.get_trade_count()
