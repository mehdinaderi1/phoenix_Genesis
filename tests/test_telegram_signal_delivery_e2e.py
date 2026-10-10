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
