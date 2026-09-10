from execution.paper_execution_engine import PaperExecutionEngine


class MockActionProposal:

    def __init__(
        self,
        action,
        status="APPROVED",
        reason=None
    ):
        self.action = action
        self.status = status
        self.reason = reason


def test_paper_buy_execution():

    proposal = MockActionProposal(
        action="BUY",
        status="APPROVED",
        reason="Valid buy signal"
    )

    engine = PaperExecutionEngine()

    result = engine.execute(
        proposal,
        price=65000,
        symbol="BTCUSDT",
        quantity=0.01
    )

    assert result.status == "EXECUTED"
    assert result.action == "BUY"
    assert result.symbol == "BTCUSDT"
    assert result.price == 65000
    assert result.quantity == 0.01


def test_paper_sell_execution():

    proposal = MockActionProposal(
        action="SELL",
        status="APPROVED",
        reason="Valid sell signal"
    )

    engine = PaperExecutionEngine()

    result = engine.execute(
        proposal,
        price=65000,
        symbol="BTCUSDT",
        quantity=0.01
    )

    assert result.status == "EXECUTED"
    assert result.action == "SELL"
    assert result.symbol == "BTCUSDT"


def test_wait_is_not_executed():

    proposal = MockActionProposal(
        action="WAIT",
        status="REJECTED",
        reason="Market conditions require monitoring"
    )

    engine = PaperExecutionEngine()

    result = engine.execute(
        proposal,
        price=65000,
        symbol="BTCUSDT"
    )

    assert result.status == "NOT_EXECUTED"
    assert result.action == "WAIT"
    assert result.reason == "Market conditions require monitoring"


def test_rejected_action_is_not_executed():

    proposal = MockActionProposal(
        action="BUY",
        status="REJECTED",
        reason="Strategy gate rejected action"
    )

    engine = PaperExecutionEngine()

    result = engine.execute(
        proposal,
        price=65000,
        symbol="BTCUSDT",
        quantity=0.01
    )

    assert result.status == "NOT_EXECUTED"
    assert result.action == "BUY"
    assert result.reason == "Strategy gate rejected action"


def test_unsupported_action_is_not_executed():

    proposal = MockActionProposal(
        action="INVALID",
        status="APPROVED"
    )

    engine = PaperExecutionEngine()

    result = engine.execute(
        proposal,
        price=65000,
        symbol="BTCUSDT"
    )

    assert result.status == "NOT_EXECUTED"
    assert result.action == "INVALID"
    assert result.reason == "Unsupported action"