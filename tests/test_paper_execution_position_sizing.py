from execution.execution_result import ExecutionResult
from execution.paper_execution_engine import PaperExecutionEngine


class ActionProposal:
    def __init__(
        self,
        action="BUY",
        status="APPROVED",
        reason="Test action"
    ):
        self.action = action
        self.status = status
        self.reason = reason


def test_execution_calculates_quantity_when_not_provided():

    engine = PaperExecutionEngine()

    proposal = ActionProposal()

    result = engine.execute(
        proposal,
        price=65000,
        symbol="BTCUSDT",
        balance=1000,
        position_size_percent=1
    )

    assert result.status == "EXECUTED"
    assert result.action == "BUY"
    assert result.symbol == "BTCUSDT"
    assert result.quantity == 10 / 65000


def test_explicit_quantity_is_preserved():

    engine = PaperExecutionEngine()

    proposal = ActionProposal()

    result = engine.execute(
        proposal,
        price=65000,
        symbol="BTCUSDT",
        quantity=0.01,
        balance=1000,
        position_size_percent=1
    )

    assert result.status == "EXECUTED"
    assert result.quantity == 0.01


def test_invalid_sizing_does_not_execute():

    engine = PaperExecutionEngine()

    proposal = ActionProposal()

    result = engine.execute(
        proposal,
        price=65000,
        symbol="BTCUSDT",
        balance=1000,
        position_size_percent=0
    )

    assert result.status == "NOT_EXECUTED"
    assert result.quantity == 0.0