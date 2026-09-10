from intelligence.action_proposal import ActionProposal
from execution.paper_trading_session import PaperTradingSession
from execution.paper_position_lifecycle import PaperPositionLifecycle


def test_paper_position_lifecycle_hold():

    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0
    )

    lifecycle = PaperPositionLifecycle(
        session
    )

    buy_proposal = ActionProposal(
        action="BUY",
        status="APPROVED",
        reason="Open BUY",
        confidence=80.0,
        symbol="BTCUSDT"
    )

    result = lifecycle.process(
        action_proposal=buy_proposal,
        price=100.0
    )

    assert result["action"] == "OPEN"
    assert session.get_position() is not None
    assert session.get_position().side == "BUY"

    wait_proposal = ActionProposal(
        action="WAIT",
        status="REJECTED",
        reason="Hold position",
        confidence=70.0,
        symbol="BTCUSDT"
    )

    result = lifecycle.process(
        action_proposal=wait_proposal,
        price=105.0
    )

    assert result["action"] == "HOLD"
    assert session.get_position() is not None
    assert session.get_position().side == "BUY"


def test_paper_position_lifecycle_close_opposite_signal():

    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0
    )

    lifecycle = PaperPositionLifecycle(
        session
    )

    buy_proposal = ActionProposal(
        action="BUY",
        status="APPROVED",
        reason="Open BUY",
        confidence=80.0,
        symbol="BTCUSDT"
    )

    lifecycle.process(
        action_proposal=buy_proposal,
        price=100.0
    )

    assert session.get_position() is not None
    assert session.get_position().side == "BUY"

    sell_proposal = ActionProposal(
        action="SELL",
        status="APPROVED",
        reason="Opposite signal",
        confidence=80.0,
        symbol="BTCUSDT"
    )

    result = lifecycle.process(
        action_proposal=sell_proposal,
        price=110.0
    )

    assert result["action"] == "CLOSE"
    assert result["realized_pnl"] == 10.0

    assert session.get_position() is None
    assert session.get_trade_count() == 1
    assert session.get_balance() == 1010.0


def test_paper_position_lifecycle_open_after_close():

    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0
    )

    lifecycle = PaperPositionLifecycle(
        session
    )

    buy_proposal = ActionProposal(
        action="BUY",
        status="APPROVED",
        reason="Open BUY",
        confidence=80.0,
        symbol="BTCUSDT"
    )

    lifecycle.process(
        action_proposal=buy_proposal,
        price=100.0
    )

    sell_proposal = ActionProposal(
        action="SELL",
        status="APPROVED",
        reason="Close BUY",
        confidence=80.0,
        symbol="BTCUSDT"
    )

    lifecycle.process(
        action_proposal=sell_proposal,
        price=110.0
    )

    assert session.get_position() is None

    # Next cycle: now SELL can open
    result = lifecycle.process(
        action_proposal=sell_proposal,
        price=110.0
    )

    assert result["action"] == "OPEN"
    assert session.get_position() is not None
    assert session.get_position().side == "SELL"

def test_paper_position_lifecycle_same_side_signal_holds():

    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0
    )

    lifecycle = PaperPositionLifecycle(
        session
    )

    buy_proposal = ActionProposal(
        action="BUY",
        status="APPROVED",
        reason="Open BUY",
        confidence=80.0,
        symbol="BTCUSDT"
    )

    first = lifecycle.process(
        action_proposal=buy_proposal,
        price=100.0
    )

    assert first["action"] == "OPEN"

    position_before = session.get_position()

    second = lifecycle.process(
        action_proposal=buy_proposal,
        price=105.0
    )

    assert second["action"] == "HOLD"

    position_after = session.get_position()

    assert position_after is position_before
    assert position_after.side == "BUY"
    assert position_after.entry_price == 100.0
    assert session.get_trade_count() == 0