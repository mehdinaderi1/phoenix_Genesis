from execution.execution_result import ExecutionResult
from execution.paper_position import PaperPosition
from execution.paper_position_manager import PaperPositionManager


def test_buy_position_pnl():

    position = PaperPosition(
        symbol="BTCUSDT",
        side="BUY",
        entry_price=65000,
        quantity=0.01
    )

    pnl = position.unrealized_pnl(66000)

    assert pnl == 10


def test_buy_position_loss():

    position = PaperPosition(
        symbol="BTCUSDT",
        side="BUY",
        entry_price=65000,
        quantity=0.01
    )

    pnl = position.unrealized_pnl(64000)

    assert pnl == -10


def test_sell_position_pnl():

    position = PaperPosition(
        symbol="BTCUSDT",
        side="SELL",
        entry_price=65000,
        quantity=0.01
    )

    pnl = position.unrealized_pnl(64000)

    assert pnl == 10


def test_sell_position_loss():

    position = PaperPosition(
        symbol="BTCUSDT",
        side="SELL",
        entry_price=65000,
        quantity=0.01
    )

    pnl = position.unrealized_pnl(66000)

    assert pnl == -10


def test_position_manager_opens_buy_position():

    execution = ExecutionResult(
        status="EXECUTED",
        action="BUY",
        symbol="BTCUSDT",
        price=65000,
        quantity=0.01
    )

    manager = PaperPositionManager()

    position = manager.open_position(execution)

    assert position is not None
    assert position.symbol == "BTCUSDT"
    assert position.side == "BUY"
    assert position.entry_price == 65000
    assert position.quantity == 0.01


def test_rejected_execution_does_not_open_position():

    execution = ExecutionResult(
        status="NOT_EXECUTED",
        action="WAIT",
        symbol="BTCUSDT",
        price=65000
    )

    manager = PaperPositionManager()

    position = manager.open_position(execution)

    assert position is None
    assert manager.get_position() is None


def test_position_manager_calculates_pnl():

    execution = ExecutionResult(
        status="EXECUTED",
        action="BUY",
        symbol="BTCUSDT",
        price=65000,
        quantity=0.01
    )

    manager = PaperPositionManager()

    manager.open_position(execution)

    pnl = manager.calculate_pnl(66000)

    assert pnl == 10


def test_position_manager_closes_position():

    execution = ExecutionResult(
        status="EXECUTED",
        action="BUY",
        symbol="BTCUSDT",
        price=65000,
        quantity=0.01
    )

    manager = PaperPositionManager()

    manager.open_position(execution)

    closed = manager.close_position()

    assert closed is not None
    assert closed.entry_price == 65000
    assert manager.get_position() is None


def test_position_close_calculates_realized_pnl():

    execution = ExecutionResult(
        status="EXECUTED",
        action="BUY",
        symbol="BTCUSDT",
        price=65000,
        quantity=0.01
    )

    manager = PaperPositionManager()

    manager.open_position(execution)

    closed = manager.close_position_with_pnl(
        current_price=66000
    )

    assert closed is not None
    assert closed["position"].symbol == "BTCUSDT"
    assert closed["position"].entry_price == 65000
    assert closed["exit_price"] == 66000
    assert closed["realized_pnl"] == 10

    assert manager.get_position() is None


def test_sell_position_close_calculates_realized_pnl():

    execution = ExecutionResult(
        status="EXECUTED",
        action="SELL",
        symbol="BTCUSDT",
        price=65000,
        quantity=0.01
    )

    manager = PaperPositionManager()

    manager.open_position(execution)

    closed = manager.close_position_with_pnl(
        current_price=64000
    )

    assert closed is not None
    assert closed["exit_price"] == 64000
    assert closed["realized_pnl"] == 10

    assert manager.get_position() is None


def test_close_without_position_returns_none():

    manager = PaperPositionManager()

    closed = manager.close_position_with_pnl(
        current_price=66000
    )

    assert closed is None

def test_cannot_open_second_position_while_position_is_open():

    first_execution = ExecutionResult(
        status="EXECUTED",
        action="BUY",
        symbol="BTCUSDT",
        price=65000,
        quantity=0.01
    )

    second_execution = ExecutionResult(
        status="EXECUTED",
        action="BUY",
        symbol="BTCUSDT",
        price=66000,
        quantity=0.01
    )

    manager = PaperPositionManager()

    first_position = manager.open_position(
        first_execution
    )

    assert first_position is not None

    second_position = manager.open_position(
        second_execution
    )

    assert second_position is None

    current_position = manager.get_position()

    assert current_position is not None
    assert current_position.entry_price == 65000
    assert current_position.quantity == 0.01