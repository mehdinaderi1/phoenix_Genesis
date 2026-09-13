import pytest

from intelligence.action_proposal import ActionProposal
from execution.paper_trading_session import PaperTradingSession


def test_paper_trading_session_buy_and_close_profit():
    proposal = ActionProposal(
        action="BUY",
        status="APPROVED",
        reason="Valid BUY setup",
        confidence=80.0,
        symbol="BTCUSDT",
        strategy="test_strategy",
        risk_status="LOW"
    )

    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0
    )

    result = session.process_action(
        action_proposal=proposal,
        price=100.0,
        symbol="BTCUSDT"
    )

    execution = result["execution_result"]
    position = result["position"]

    assert execution.status == "EXECUTED"
    assert execution.action == "BUY"
    assert execution.symbol == "BTCUSDT"
    assert execution.price == 100.0
    assert execution.quantity == pytest.approx(1.0)

    assert position is not None
    assert position.side == "BUY"
    assert position.entry_price == 100.0
    assert position.quantity == pytest.approx(1.0)

    closed = session.close_position(
        exit_price=110.0
    )

    assert closed is not None
    assert closed["realized_pnl"] == pytest.approx(10.0)

    assert session.get_position() is None
    assert session.get_balance() == pytest.approx(1010.0)
    assert session.get_total_pnl() == pytest.approx(10.0)
    assert session.get_trade_count() == 1


def test_paper_trading_session_sell_and_close_profit():
    proposal = ActionProposal(
        action="SELL",
        status="APPROVED",
        reason="Valid SELL setup",
        confidence=80.0,
        symbol="BTCUSDT",
        strategy="test_strategy",
        risk_status="LOW"
    )

    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0
    )

    result = session.process_action(
        action_proposal=proposal,
        price=100.0,
        symbol="BTCUSDT"
    )

    execution = result["execution_result"]
    position = result["position"]

    assert execution.status == "EXECUTED"
    assert execution.action == "SELL"
    assert execution.quantity == pytest.approx(1.0)

    assert position is not None
    assert position.side == "SELL"
    assert position.entry_price == 100.0
    assert position.quantity == pytest.approx(1.0)

    closed = session.close_position(
        exit_price=90.0
    )

    assert closed is not None
    assert closed["realized_pnl"] == pytest.approx(10.0)

    assert session.get_position() is None
    assert session.get_balance() == pytest.approx(1010.0)
    assert session.get_total_pnl() == pytest.approx(10.0)
    assert session.get_trade_count() == 1


def test_paper_trading_session_wait_does_not_open_position():
    proposal = ActionProposal(
        action="WAIT",
        status="REJECTED",
        reason="Market conditions require monitoring",
        confidence=70.0,
        symbol="BTCUSDT",
        risk_status="MEDIUM"
    )

    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0
    )

    result = session.process_action(
        action_proposal=proposal,
        price=65000.0,
        symbol="BTCUSDT"
    )

    execution = result["execution_result"]

    assert execution.status == "NOT_EXECUTED"
    assert execution.action == "WAIT"

    assert result["position"] is None

    assert session.get_position() is None
    assert session.get_balance() == pytest.approx(1000.0)
    assert session.get_total_pnl() == pytest.approx(0.0)
    assert session.get_trade_count() == 0


def test_paper_trading_session_no_position_close():
    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0
    )

    closed = session.close_position(
        exit_price=110.0
    )

    assert closed is None

    assert session.get_position() is None
    assert session.get_balance() == pytest.approx(1000.0)
    assert session.get_total_pnl() == pytest.approx(0.0)
    assert session.get_trade_count() == 0

def test_paper_trading_session_multiple_trade_cycles():
    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0
    )

    buy_proposal = ActionProposal(
        action="BUY",
        status="APPROVED",
        reason="BUY setup",
        confidence=80.0,
        symbol="BTCUSDT",
        strategy="test_strategy",
        risk_status="LOW"
    )

    buy_result = session.process_action(
        action_proposal=buy_proposal,
        price=100.0,
        symbol="BTCUSDT"
    )

    assert buy_result["execution_result"].status == "EXECUTED"
    assert buy_result["position"] is not None

    buy_closed = session.close_position(
        exit_price=110.0
    )

    assert buy_closed is not None
    assert buy_closed["realized_pnl"] == pytest.approx(10.0)

    assert session.get_position() is None
    assert session.get_balance() == pytest.approx(1010.0)
    assert session.get_total_pnl() == pytest.approx(10.0)
    assert session.get_trade_count() == 1

    sell_proposal = ActionProposal(
        action="SELL",
        status="APPROVED",
        reason="SELL setup",
        confidence=80.0,
        symbol="BTCUSDT",
        strategy="test_strategy",
        risk_status="LOW"
    )

    sell_result = session.process_action(
        action_proposal=sell_proposal,
        price=100.0,
        symbol="BTCUSDT"
    )

    assert sell_result["execution_result"].status == "EXECUTED"
    assert sell_result["position"] is not None
    assert sell_result["position"].side == "SELL"

    sell_closed = session.close_position(
        exit_price=110.0
    )

    assert sell_closed is not None
    assert sell_closed["realized_pnl"] == pytest.approx(-10.1)

    assert session.get_position() is None
    assert session.get_balance() == pytest.approx(999.9)
    assert session.get_total_pnl() == pytest.approx(-0.1)
    assert session.get_trade_count() == 2

def test_paper_close_triggers_real_outcome_learning():

    from types import SimpleNamespace

    from intelligence.flow import IntelligenceFlow
    from execution.paper_trading_session import PaperTradingSession

    flow = IntelligenceFlow()

    flow.enable_inline_outcome_learning = False

    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=1.0,
        outcome_bridge=flow.decision_outcome_bridge
    )

    decision = SimpleNamespace(
        action="PREPARE_LONG",
        regime="RANGING",
        signal="BUY",
        risk="LOW",
        confidence=80,
        trace={},
        strategy={"name": "PAPER_TEST_STRATEGY"},
        champion_strategy=None
    )

    buy = SimpleNamespace(action="BUY")
    sell = SimpleNamespace(action="SELL")

    from execution.paper_trading_cycle import PaperTradingCycle

    cycle = PaperTradingCycle(session)

    opened = cycle.process(
        action_proposal=buy,
        price=65000.0,
        symbol="BTCUSDT",
        decision=decision
    )

    assert opened["action"] == "OPEN"
    assert session.get_position() is not None
    assert len(flow.experience_memory.experiences) == 0

    closed = cycle.process(
        action_proposal=sell,
        price=66000.0,
        symbol="BTCUSDT"
    )

    assert closed["action"] == "CLOSE"
    assert closed["realized_pnl"] > 0
    assert closed["learning_result"] is not None

    assert len(flow.experience_memory.experiences) == 1

    experience = flow.experience_memory.experiences[0]

    assert experience.strategy == "PAPER_TEST_STRATEGY"
    assert experience.success is True
