from datetime import datetime, timezone

from notifications.dispatcher import NotificationDispatcher
from notifications.signal_outbox import SignalOutbox


class FakeSender:
    def __init__(self, should_fail=False):
        self.should_fail = should_fail
        self.messages = []

    def send_message(self, message):
        self.messages.append(message)
        if self.should_fail:
            raise RuntimeError("simulated Telegram outage")
        return {"message_id": 1}


def add_signal(outbox, signal_id="sig-dispatch-001"):
    outbox.record_signal(
        {
            "signal_id": signal_id,
            "symbol": "BTCUSDT",
            "action": "BUY",
            "status": "APPROVED",
            "reference_price": 65000.0,
            "generated_at": "2026-10-09T10:00:00Z",
        },
        f"Phoenix signal {signal_id}",
    )


def test_dispatch_marks_message_sent_after_success(tmp_path):
    outbox = SignalOutbox(tmp_path / "dispatch.db")
    add_signal(outbox)
    sender = FakeSender()
    clock = lambda: datetime(2026, 10, 9, 10, 1, tzinfo=timezone.utc)
    dispatcher = NotificationDispatcher(outbox, sender, clock)

    result = dispatcher.dispatch_due_messages()

    assert result == {"sent": 1, "failed": 0}
    assert sender.messages == ["Phoenix signal sig-dispatch-001"]
    message = outbox.get_message("sig-dispatch-001")
    assert message["status"] == "SENT"
    assert message["sent_at"] == "2026-10-09T10:01:00Z"


def test_dispatch_keeps_failed_message_pending_and_schedules_retry(tmp_path):
    outbox = SignalOutbox(tmp_path / "dispatch.db")
    add_signal(outbox, "sig-dispatch-fail")
    sender = FakeSender(should_fail=True)
    clock = lambda: datetime(2026, 10, 9, 10, 1, tzinfo=timezone.utc)
    dispatcher = NotificationDispatcher(outbox, sender, clock)

    result = dispatcher.dispatch_due_messages()

    assert result == {"sent": 0, "failed": 1}
    message = outbox.get_message("sig-dispatch-fail")
    assert message["status"] == "PENDING"
    assert message["attempts"] == 1
    assert message["last_error"] == "RuntimeError: simulated Telegram outage"
    assert message["next_attempt_at"] == "2026-10-09T10:01:05Z"


def test_dispatch_skips_messages_before_retry_deadline(tmp_path):
    outbox = SignalOutbox(tmp_path / "dispatch.db")
    add_signal(outbox, "sig-dispatch-wait")
    outbox.mark_failed(
        "sig-dispatch-wait",
        "temporary failure",
        "2026-10-09T10:02:00Z",
    )
    sender = FakeSender()
    clock = lambda: datetime(2026, 10, 9, 10, 1, tzinfo=timezone.utc)
    dispatcher = NotificationDispatcher(outbox, sender, clock)

    result = dispatcher.dispatch_due_messages()

    assert result == {"sent": 0, "failed": 0}
    assert sender.messages == []
    assert outbox.get_message("sig-dispatch-wait")["status"] == "PENDING"
