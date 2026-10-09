from execution.paper_trading_session import PaperTradingSession
from intelligence.action_proposal import ActionProposal

def test_paper_session_checkpoint_restores_open_position_and_continues():
    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0
    )

    buy_proposal = ActionProposal(
        action="BUY",
        status="APPROVED",
        reason="Open BUY",
        confidence=80.0,
        symbol="BTCUSDT"
    )

    opened = session.process_action(
        action_proposal=buy_proposal,
        price=100.0,
        symbol="BTCUSDT"
    )

    assert opened["position"] is not None
    assert session.get_position().side == "BUY"
    assert session.get_position().entry_price == 100.0

    checkpoint = session.build_checkpoint()

    assert checkpoint["session_id"] == session.session_id
    assert checkpoint["balance"] == 1000.0
    assert checkpoint["position"]["side"] == "BUY"
    assert checkpoint["position"]["entry_price"] == 100.0

    restored = PaperTradingSession.from_checkpoint(checkpoint)

    assert restored.session_id == session.session_id
    assert restored.get_balance() == 1000.0
    assert restored.get_total_pnl() == 0.0
    assert restored.get_trade_count() == 0

    position = restored.get_position()
    assert position is not None
    assert position.symbol == "BTCUSDT"
    assert position.side == "BUY"
    assert position.entry_price == 100.0
    assert position.quantity == session.get_position().quantity

    closed = restored.close_position(exit_price=110.0)

    assert closed is not None
    assert closed["realized_pnl"] == 10.0
    assert restored.get_position() is None
    assert restored.get_trade_count() == 1
    assert restored.get_balance() == 1010.0
    assert restored.get_total_pnl() == 10.0


def test_checkpoint_restores_open_position_decision():
    from intelligence.decision import DecisionResult

    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0
    )

    decision = DecisionResult(
        action="BUY",
        reason="Checkpoint recovery test",
        confidence=85.0,
        champion_strategy={"name": "test_strategy"},
        metadata={"source": "checkpoint_test"}
    )

    proposal = ActionProposal(
        action="BUY",
        status="APPROVED",
        reason="Open BUY",
        confidence=85.0,
        symbol="BTCUSDT"
    )

    opened = session.process_action(
        action_proposal=proposal,
        price=100.0,
        symbol="BTCUSDT",
        decision=decision
    )

    assert opened["position"] is not None

    checkpoint = session.build_checkpoint()
    restored = PaperTradingSession.from_checkpoint(checkpoint)

    restored_decision = restored.get_position().decision

    assert isinstance(restored_decision, DecisionResult)
    assert restored_decision.action == "BUY"
    assert restored_decision.reason == "Checkpoint recovery test"
    assert restored_decision.champion_strategy == {"name": "test_strategy"}
    assert restored_decision.metadata == {"source": "checkpoint_test"}
