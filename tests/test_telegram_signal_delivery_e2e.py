from datetime import datetime, timezone
from types import SimpleNamespace

from notifications.dispatcher import NotificationDispatcher
from notifications.signal_outbox import SignalOutbox
from notifications.signal_publisher import SignalPublisher


class FakeSender:
    def __init__(self):
        self.messages = []

    def send_message(self, message):
        self.messages.append(message)
        return {"message_id": 123}


def test_approved_signal_flows_from_publisher_to_sent_outbox(tmp_path):
    outbox = SignalOutbox(tmp_path / "telegram-e2e.db")
    publisher = SignalPublisher(outbox)

    proposal = SimpleNamespace(
        action="BUY",
        status="APPROVED",
        reason="E2E integration test",
        confidence=0.91,
        risk_status="ACCEPTABLE",
    )
    observation = SimpleNamespace(
        symbol="BTCUSDT",
        price=65000.0,
        timestamp="2026-10-09T12:00:00+00:00",
    )
    boundaries = {
        "5m": {
            "candle_start": 1_760_000_000,
            "next_boundary": 1_760_000_300,
            "duration_seconds": 300,
            "age_seconds": 10,
            "is_closed": False,
        }
    }

    signal = publisher.publish(
        proposal,
        observation,
        boundaries,
        generated_at="2026-10-09T12:01:00+00:00",
    )

    assert signal is not None
    assert signal["action"] == "BUY"
    assert signal["status"] == "APPROVED"
    assert signal["reference_price"] == 65000.0
    assert signal["observed_at"] == "2026-10-09T12:00:00Z"
    assert signal["generated_at"] == "2026-10-09T12:01:00Z"

    stored_signal = outbox.get_signal(signal["signal_id"])
    stored_message = outbox.get_message(signal["signal_id"])

    assert stored_signal == signal
    assert stored_message["status"] == "PENDING"
    assert stored_message["payload"] in [
        item["payload"] for item in outbox.get_pending_messages()
    ]

    sender = FakeSender()
    fixed_time = datetime(2026, 10, 9, 12, 5, tzinfo=timezone.utc)
    dispatcher = NotificationDispatcher(
        outbox=outbox,
        sender=sender,
        clock=lambda: fixed_time,
    )

    result = dispatcher.dispatch_due_messages()

    assert result == {"sent": 1, "failed": 0}
    assert sender.messages == [stored_message["payload"]]

    final_message = outbox.get_message(signal["signal_id"])
    final_signal = outbox.get_signal(signal["signal_id"])

    assert final_message["status"] == "SENT"
    assert final_message["sent_at"] == "2026-10-09T12:05:00Z"
    assert final_message["attempts"] == 0
    assert final_signal["observed_at"] == "2026-10-09T12:00:00Z"
    assert final_signal["generated_at"] == "2026-10-09T12:01:00Z"
    assert final_signal["reference_price"] == 65000.0
    assert outbox.get_pending_messages() == []


class FailingOnceSender:
    def __init__(self):
        self.messages = []
        self.failed_once = False

    def send_message(self, message):
        self.messages.append(message)
        if not self.failed_once:
            self.failed_once = True
            raise RuntimeError("simulated Telegram outage")
        return {"message_id": 456}


def test_signal_reference_survives_failed_delivery_retry_and_reopen(tmp_path):
    db_path = tmp_path / "telegram-retry-e2e.db"
    outbox = SignalOutbox(db_path)
    publisher = SignalPublisher(outbox)

    proposal = SimpleNamespace(
        action="BUY",
        status="APPROVED",
        reason="Retry persistence test",
        confidence=0.91,
        risk_status="ACCEPTABLE",
    )
    observation = SimpleNamespace(
        symbol="BTCUSDT",
        price=65000.0,
        timestamp="2026-10-09T12:00:00+00:00",
    )
    boundaries = {
        "5m": {
            "candle_start": 1_760_000_000,
            "next_boundary": 1_760_000_300,
            "duration_seconds": 300,
            "age_seconds": 10,
            "is_closed": False,
        }
    }

    signal = publisher.publish(
        proposal,
        observation,
        boundaries,
        generated_at="2026-10-09T12:01:00+00:00",
    )
    assert signal is not None
    signal_id = signal["signal_id"]
    original_signal = outbox.get_signal(signal_id)
    original_message = outbox.get_message(signal_id)
    assert original_signal["reference_price"] == 65000.0
    assert original_signal["generated_at"] == "2026-10-09T12:01:00Z"

    sender = FailingOnceSender()
    first_dispatcher = NotificationDispatcher(
        outbox=outbox,
        sender=sender,
        clock=lambda: datetime(2026, 10, 9, 12, 5, tzinfo=timezone.utc),
    )

    first_result = first_dispatcher.dispatch_due_messages()
    assert first_result == {"sent": 0, "failed": 1}

    failed_message = outbox.get_message(signal_id)
    assert failed_message["status"] == "PENDING"
    assert failed_message["attempts"] == 1
    assert failed_message["next_attempt_at"] == "2026-10-09T12:05:05Z"
    assert outbox.get_signal(signal_id) == original_signal

    reopened_outbox = SignalOutbox(db_path)
    persisted_signal = reopened_outbox.get_signal(signal_id)
    persisted_message = reopened_outbox.get_message(signal_id)
    assert persisted_signal == original_signal
    assert persisted_message["status"] == "PENDING"
    assert persisted_message["attempts"] == 1

    retry_dispatcher = NotificationDispatcher(
        outbox=reopened_outbox,
        sender=sender,
        clock=lambda: datetime(2026, 10, 9, 12, 5, 5, tzinfo=timezone.utc),
    )
    retry_result = retry_dispatcher.dispatch_due_messages()

    assert retry_result == {"sent": 1, "failed": 0}
    final_signal = reopened_outbox.get_signal(signal_id)
    final_message = reopened_outbox.get_message(signal_id)

    assert final_signal == original_signal
    assert final_signal["reference_price"] == 65000.0
    assert final_signal["observed_at"] == "2026-10-09T12:00:00Z"
    assert final_signal["generated_at"] == "2026-10-09T12:01:00Z"
    assert final_message["status"] == "SENT"
    assert final_message["attempts"] == 1
    assert final_message["sent_at"] == "2026-10-09T12:05:05Z"
    assert sender.messages == [
        original_message["payload"],
        original_message["payload"],
    ]
    assert reopened_outbox.get_pending_messages() == []
