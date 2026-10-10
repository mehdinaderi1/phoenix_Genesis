from datetime import datetime, timedelta, timezone

from notifications.signal_outbox import SignalOutbox
from notifications.telegram_sender import TelegramSender


class NotificationDispatcher:
    """Dispatch persisted outbox messages without affecting trading logic."""

    RETRY_DELAYS_SECONDS = (5, 15, 60, 300, 900)

    def __init__(self, outbox=None, sender=None, clock=None):
        self.outbox = outbox or SignalOutbox("data/phoenix_notifications.db")
        self.sender = sender or TelegramSender()
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def _now(self):
        value = self.clock()
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    def dispatch_due_messages(self):
        now = self._now()
        as_of = now.isoformat(timespec="seconds").replace("+00:00", "Z")
        messages = self.outbox.get_pending_messages(as_of=as_of)

        results = {"sent": 0, "failed": 0}
        for message in messages:
            signal_id = message["signal_id"]
            try:
                self.sender.send_message(message["payload"])
            except Exception as exc:
                current = self.outbox.get_message(signal_id)
                attempt_number = current["attempts"] + 1
                delay_index = min(
                    attempt_number - 1,
                    len(self.RETRY_DELAYS_SECONDS) - 1,
                )
                retry_at = self._now() + timedelta(
                    seconds=self.RETRY_DELAYS_SECONDS[delay_index]
                )
                retry_text = retry_at.isoformat(
                    timespec="seconds"
                ).replace("+00:00", "Z")
                error_text = f"{type(exc).__name__}: {exc}"[:500]
                self.outbox.mark_failed(
                    signal_id,
                    error_text,
                    retry_text,
                )
                results["failed"] += 1
                continue

            sent_at = self._now().isoformat(
                timespec="seconds"
            ).replace("+00:00", "Z")
            self.outbox.mark_sent(signal_id, sent_at)
            results["sent"] += 1

        return results
