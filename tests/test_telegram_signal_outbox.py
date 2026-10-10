import sqlite3
from notifications.signal_outbox import SignalOutbox


def test_signal_and_outbox_are_persisted_atomically(tmp_path):
    store = SignalOutbox(tmp_path / "phoenix_test.db")
    signal = {
        "signal_id": "sig-001",
        "symbol": "BTCUSDT",
        "action": "BUY",
        "status": "APPROVED",
        "reference_price": 65000.0,
        "generated_at": "2026-10-09T10:00:00Z",
    }
    message = "Phoenix signal sig-001"

    store.record_signal(signal, message)

    assert store.get_signal("sig-001")["reference_price"] == 65000.0
    pending = store.get_pending_messages()
    assert len(pending) == 1
    assert pending[0]["signal_id"] == "sig-001"
    assert pending[0]["payload"] == message
    assert pending[0]["status"] == "PENDING"


def test_pending_message_survives_store_reopen(tmp_path):
    db_path = tmp_path / "phoenix_test.db"
    store = SignalOutbox(db_path)
    store.record_signal({
        "signal_id": "sig-002",
        "symbol": "BTCUSDT",
        "action": "SELL",
        "status": "APPROVED",
        "reference_price": 65100.0,
        "generated_at": "2026-10-09T10:01:00Z",
    }, "Phoenix signal sig-002")

    reopened = SignalOutbox(db_path)
    pending = reopened.get_pending_messages()
    assert [item["signal_id"] for item in pending] == ["sig-002"]


def test_mark_sent_requires_explicit_success_timestamp(tmp_path):
    store = SignalOutbox(tmp_path / "phoenix_test.db")
    store.record_signal({
        "signal_id": "sig-003",
        "symbol": "BTCUSDT",
        "action": "BUY",
        "status": "APPROVED",
        "reference_price": 65200.0,
        "generated_at": "2026-10-09T10:02:00Z",
    }, "Phoenix signal sig-003")

    store.mark_sent("sig-003", "2026-10-09T10:02:05Z")

    assert store.get_pending_messages() == []
    assert store.get_message("sig-003")["sent_at"] == "2026-10-09T10:02:05Z"


def test_failed_outbox_insert_rolls_back_signal_record(tmp_path):
    store = SignalOutbox(tmp_path / "phoenix_test.db")
    signal = {
        "signal_id": "sig-rollback",
        "symbol": "BTCUSDT",
        "action": "BUY",
        "status": "APPROVED",
        "reference_price": 65000.0,
        "generated_at": "2026-10-09T10:03:00Z",
    }
    store.record_signal(signal, "first message")

    try:
        store.record_signal(signal, "duplicate message")
        assert False, "Duplicate signal should violate the primary key"
    except sqlite3.IntegrityError:
        pass

    assert store.get_signal("sig-rollback") is not None
    assert len([
        item for item in store.get_pending_messages()
        if item["signal_id"] == "sig-rollback"
    ]) == 1


def test_outbox_failure_rolls_back_new_signal(tmp_path):
    db_path = tmp_path / "phoenix_test.db"
    store = SignalOutbox(db_path)
    with store._connect() as connection:
        connection.execute("""
            CREATE TRIGGER reject_outbox_insert
            BEFORE INSERT ON notification_outbox
            BEGIN
                SELECT RAISE(ABORT, 'simulated outbox failure');
            END
        """)

    signal = {
        "signal_id": "sig-atomic",
        "symbol": "BTCUSDT",
        "action": "BUY",
        "status": "APPROVED",
        "reference_price": 65000.0,
        "generated_at": "2026-10-09T10:04:00Z",
    }

    try:
        store.record_signal(signal, "message that must not be queued")
        assert False, "Outbox failure should abort signal recording"
    except sqlite3.IntegrityError:
        pass

    assert store.get_signal("sig-atomic") is None
    assert store.get_pending_messages() == []


def test_failed_delivery_persists_retry_state(tmp_path):
    db_path = tmp_path / "phoenix_test.db"
    store = SignalOutbox(db_path)
    store.record_signal({
        "signal_id": "sig-retry",
        "symbol": "BTCUSDT",
        "action": "SELL",
        "status": "APPROVED",
        "reference_price": 65100.0,
        "generated_at": "2026-10-09T10:05:00Z",
    }, "Phoenix signal sig-retry")

    store.mark_failed(
        "sig-retry",
        "simulated network outage",
        "2026-10-09T10:06:00Z",
    )

    reopened = SignalOutbox(db_path)
    message = reopened.get_message("sig-retry")
    assert message["attempts"] == 1
    assert message["last_error"] == "simulated network outage"
    assert message["next_attempt_at"] == "2026-10-09T10:06:00Z"


def test_pending_messages_can_be_filtered_by_retry_deadline(tmp_path):
    store = SignalOutbox(tmp_path / "phoenix_test.db")
    store.record_signal({
        "signal_id": "sig-future-retry",
        "symbol": "BTCUSDT",
        "action": "BUY",
        "status": "APPROVED",
        "reference_price": 65000.0,
        "generated_at": "2026-10-09T10:07:00Z",
    }, "Phoenix signal sig-future-retry")
    store.mark_failed(
        "sig-future-retry",
        "temporary network error",
        "2026-10-09T10:10:00Z",
    )

    assert store.get_pending_messages(as_of="2026-10-09T10:09:59Z") == []
    due = store.get_pending_messages(as_of="2026-10-09T10:10:00Z")
    assert len(due) == 1
    assert due[0]["signal_id"] == "sig-future-retry"

def test_wait_or_unapproved_signal_is_rejected(tmp_path):
    store = SignalOutbox(tmp_path / "phoenix_test.db")

    invalid_signals = [
        {
            "signal_id": "sig-wait",
            "symbol": "BTCUSDT",
            "action": "WAIT",
            "status": "APPROVED",
            "reference_price": 65000.0,
            "generated_at": "2026-10-09T10:11:00Z",
        },
        {
            "signal_id": "sig-unapproved",
            "symbol": "BTCUSDT",
            "action": "BUY",
            "status": "REJECTED",
            "reference_price": 65000.0,
            "generated_at": "2026-10-09T10:12:00Z",
        },
    ]

    for signal in invalid_signals:
        try:
            store.record_signal(signal, "must not be published")
            assert False, f"Invalid signal was accepted: {signal['signal_id']}"
        except ValueError:
            pass

    assert store.get_pending_messages() == []
