from intelligence.action_proposal import ActionProposal
from execution.paper_trading_session import PaperTradingSession


def test_session_record_contains_basic_session_data():

    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0
    )

    action = ActionProposal(
        action="BUY",
        status="APPROVED",
        confidence=80,
        symbol="BTCUSDT",
        strategy="test_strategy"
    )

    session.process_action(
        action_proposal=action,
        price=100.0,
        symbol="BTCUSDT"
    )

    session.close_position(
        exit_price=110.0
    )

    record = session.get_session_record()

    assert record["initial_balance"] == 1000.0
    assert record["position_size_percent"] == 10.0
    assert record["trade_count"] == 1
    assert record["total_pnl"] == 10.0
    assert len(record["trades"]) == 1
    assert record["trades"][0]["symbol"] == "BTCUSDT"
    assert record["trades"][0]["realized_pnl"] == 10.0
from execution.paper_trading_session import PaperTradingSession


def test_empty_session_record_is_serializable():
    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0
    )

    record = session.get_session_record()

    assert record["initial_balance"] == 1000.0
    assert record["balance"] == 1000.0
    assert record["total_pnl"] == 0.0
    assert record["trade_count"] == 0
    assert record["trades"] == []
def test_session_record_contains_all_trades():
    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0
    )

    buy = ActionProposal(
        action="BUY",
        status="APPROVED",
        confidence=80,
        symbol="BTCUSDT",
        strategy="test_strategy"
    )

    sell = ActionProposal(
        action="SELL",
        status="APPROVED",
        confidence=80,
        symbol="BTCUSDT",
        strategy="test_strategy"
    )

    session.process_action(
        action_proposal=buy,
        price=100.0,
        symbol="BTCUSDT"
    )

    session.close_position(
        exit_price=110.0
    )

    session.process_action(
        action_proposal=sell,
        price=100.0,
        symbol="BTCUSDT"
    )

    session.close_position(
        exit_price=90.0
    )

    record = session.get_session_record()

    assert record["trade_count"] == 2
    assert len(record["trades"]) == 2
    assert record["trades"][0]["realized_pnl"] == 10.0
    assert record["trades"][1]["realized_pnl"] == 10.1
import json

from execution.paper_session_archive import PaperSessionArchive
from execution.paper_trading_session import PaperTradingSession
from intelligence.action_proposal import ActionProposal


def test_runtime_session_record_can_be_archived_and_loaded(
    tmp_path
):
    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0
    )

    action = ActionProposal(
        action="BUY",
        status="APPROVED",
        confidence=80,
        symbol="BTCUSDT",
        strategy="test_strategy"
    )

    session.process_action(
        action_proposal=action,
        price=100.0,
        symbol="BTCUSDT"
    )

    session.close_position(
        exit_price=110.0
    )

    record = session.get_session_record()

    archive = PaperSessionArchive(
        tmp_path
    )

    archive.save(
        "runtime-session-001",
        record
    )

    loaded = archive.load(
        "runtime-session-001"
    )

    assert loaded == record
    assert loaded["initial_balance"] == 1000.0
    assert loaded["balance"] == 1010.0
    assert loaded["trade_count"] == 1
    assert loaded["total_pnl"] == 10.0
    assert loaded["trades"][0]["symbol"] == "BTCUSDT"
    assert loaded["trades"][0]["realized_pnl"] == 10.0

    json.dumps(loaded)
def test_session_record_contains_session_id():
    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0
    )

    record = session.get_session_record()

    assert "session_id" in record
    assert record["session_id"] == session.session_id
    assert record["session_id"]
def test_runtime_session_uses_its_own_id_for_archive(tmp_path):
    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0
    )

    record = session.get_session_record()

    archive = PaperSessionArchive(
        tmp_path
    )

    archive.save(
        session.session_id,
        record
    )

    assert session.session_id in archive.list()

    loaded = archive.load(
        session.session_id
    )

    assert loaded["session_id"] == session.session_id
    assert loaded == record
def test_runtime_session_uses_its_own_id_for_archive(tmp_path):
    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0
    )

    record = session.get_session_record()

    archive = PaperSessionArchive(
        tmp_path
    )

    archive.save(
        session.session_id,
        record
    )

    assert session.session_id in archive.list()

    loaded = archive.load(
        session.session_id
    )

    assert loaded["session_id"] == session.session_id
    assert loaded == record
