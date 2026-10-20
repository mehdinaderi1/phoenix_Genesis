from dataclasses import asdict
from uuid import uuid4

from execution.paper_execution_engine import PaperExecutionEngine
from execution.paper_position_manager import PaperPositionManager
from execution.paper_position import PaperPosition
from execution.paper_portfolio import PaperPortfolio
from execution.paper_trade_history import PaperTradeHistory
from execution.paper_trade_record import PaperTradeRecord
from intelligence.decision import DecisionResult


class PaperTradingSession:

    def __init__(
        self,
        initial_balance=1000.0,
        position_size_percent=1.0,
        execution_engine=None,
        position_manager=None,
        portfolio=None,
        trade_history=None,
        session_id=None,
        outcome_bridge=None
    ):
        self.session_id = session_id or str(uuid4())
        self.initial_balance = initial_balance
        self.position_size_percent = position_size_percent
        self.outcome_bridge = outcome_bridge
        self.execution_engine = execution_engine or PaperExecutionEngine()
        self.position_manager = position_manager or PaperPositionManager()
        self.portfolio = portfolio or PaperPortfolio.create(
            initial_balance=initial_balance
        )
        self.trade_history = trade_history or PaperTradeHistory()

    def process_action(
        self,
        action_proposal,
        price,
        symbol="BTCUSDT",
        decision=None
    ):
        execution_result = self.execution_engine.execute(
            action_proposal=action_proposal,
            price=price,
            symbol=symbol,
            balance=self.portfolio.get_balance(),
            position_size_percent=self.position_size_percent
        )

        position = self.position_manager.open_position(
            execution_result,
            decision=decision
        )

        return {
            "execution_result": execution_result,
            "position": position,
            "portfolio": self.portfolio,
            "trade_history": self.trade_history
        }

    def close_position(self, exit_price):
        closed = self.position_manager.close_position_with_pnl(
            current_price=exit_price
        )

        if closed is None:
            return None

        realized_pnl = closed["realized_pnl"]
        self.portfolio.apply_realized_pnl(realized_pnl)

        trade = self.trade_history.add_trade(
            position=closed["position"],
            exit_price=closed["exit_price"],
            realized_pnl=realized_pnl
        )

        learning_result = None
        position = closed["position"]
        decision = getattr(position, "decision", None)

        if self.outcome_bridge is not None and decision is not None:
            learning_result = self.outcome_bridge.process(
                decision=decision,
                entry_price=position.entry_price,
                exit_price=closed["exit_price"]
            )

        return {
            "position": position,
            "exit_price": closed["exit_price"],
            "realized_pnl": realized_pnl,
            "trade": trade,
            "portfolio": self.portfolio,
            "trade_history": self.trade_history,
            "learning_result": learning_result
        }

    def get_position(self):
        return self.position_manager.get_position()

    def get_balance(self):
        return self.portfolio.get_balance()

    def get_total_pnl(self):
        return self.portfolio.get_total_pnl()

    def get_trade_count(self):
        return self.trade_history.get_trade_count()

    def build_checkpoint(self):
        position = self.get_position()

        return {
            "session_id": self.session_id,
            "initial_balance": self.initial_balance,
            "position_size_percent": self.position_size_percent,
            "balance": self.get_balance(),
            "position": (
                {
                    "symbol": position.symbol,
                    "side": position.side,
                    "entry_price": position.entry_price,
                    "quantity": position.quantity,
                    "sl": getattr(position, "sl", None),
                    "tp": getattr(position, "tp", None),
                    "opened_at": getattr(position, "opened_at", None),
                    "decision": (
                        position.decision.to_dict()
                        if position.decision is not None
                        and hasattr(position.decision, "to_dict")
                        else None
                    )
                }
                if position is not None
                else None
            ),
                
            "trades": [
                asdict(trade)
                for trade in self.trade_history.get_trades()
            ]
        }

    @classmethod
    def from_checkpoint(cls, checkpoint):
        portfolio = PaperPortfolio(
            initial_balance=checkpoint["initial_balance"],
            balance=checkpoint["balance"]
        )

        position_manager = PaperPositionManager()
        position_data = checkpoint.get("position")

        if position_data is not None:
            position_manager.position = PaperPosition(
                symbol=position_data["symbol"],
                side=position_data["side"],
                entry_price=position_data["entry_price"],
                quantity=position_data["quantity"],
                sl=position_data.get("sl"),
                tp=position_data.get("tp"),
                opened_at=position_data.get("opened_at"),
                decision=(
                    DecisionResult(**position_data["decision"])
                    if position_data.get("decision") is not None
                    else None
                )
            )

        trade_history = PaperTradeHistory()
        trade_history.trades = [
            PaperTradeRecord(**trade)
            for trade in checkpoint.get("trades", [])
        ]

        return cls(
            initial_balance=checkpoint["initial_balance"],
            position_size_percent=checkpoint["position_size_percent"],
            position_manager=position_manager,
            portfolio=portfolio,
            trade_history=trade_history,
            session_id=checkpoint["session_id"]
        )

    def get_session_record(self):
        return {
            "session_id": self.session_id,
            "initial_balance": self.initial_balance,
            "position_size_percent": self.position_size_percent,
            "balance": self.get_balance(),
            "total_pnl": self.get_total_pnl(),
            "trade_count": self.get_trade_count(),
            "trades": [
                asdict(trade)
                for trade in self.trade_history.get_trades()
            ]
        }
