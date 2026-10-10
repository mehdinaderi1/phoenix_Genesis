import json
import sqlite3
from pathlib import Path


class SignalOutbox:
    def __init__(self, db_path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS signal_journal (
                    signal_id TEXT PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    action TEXT NOT NULL,
                    status TEXT NOT NULL,
                    reference_price REAL,
                    generated_at TEXT NOT NULL,
                    payload TEXT NOT NULL
                )
            """)
            connection.execute("""
                CREATE TABLE IF NOT EXISTS notification_outbox (
                    message_id TEXT PRIMARY KEY,
                    signal_id TEXT NOT NULL UNIQUE,
                    payload TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'PENDING',
                    attempts INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    sent_at TEXT,
                    last_error TEXT,
                    next_attempt_at TEXT,
                    FOREIGN KEY(signal_id) REFERENCES signal_journal(signal_id)
                )
            """)
            columns = {
                row["name"]
                for row in connection.execute(
                    "PRAGMA table_info(notification_outbox)"
                ).fetchall()
            }
            if "next_attempt_at" not in columns:
                connection.execute(
                    "ALTER TABLE notification_outbox ADD COLUMN next_attempt_at TEXT"
                )

    def _connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def record_signal(self, signal, message):
        required = ("signal_id", "symbol", "action", "status", "generated_at")
        missing = [key for key in required if not signal.get(key)]
        if missing:
            raise ValueError(f"Missing required signal fields: {missing}")
        if signal["action"] not in {"BUY", "SELL"} or signal["status"] != "APPROVED":
            raise ValueError("Only APPROVED BUY or SELL signals can be recorded for publication")

        with self._connect() as connection:
            connection.execute(
                "INSERT INTO signal_journal "
                "(signal_id, symbol, action, status, reference_price, generated_at, payload) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    signal["signal_id"], signal["symbol"], signal["action"],
                    signal["status"], signal.get("reference_price"),
                    signal["generated_at"], json.dumps(signal, ensure_ascii=False),
                ),
            )
            connection.execute(
                "INSERT INTO notification_outbox (message_id, signal_id, payload) "
                "VALUES (?, ?, ?)",
                (signal["signal_id"], signal["signal_id"], message),
            )

    def get_signal(self, signal_id):
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload FROM signal_journal WHERE signal_id = ?",
                (signal_id,),
            ).fetchone()
        return json.loads(row["payload"]) if row else None

    def get_pending_messages(self, as_of=None):
        with self._connect() as connection:
            if as_of is None:
                rows = connection.execute(
                    "SELECT * FROM notification_outbox "
                    "WHERE status = 'PENDING' "
                    "ORDER BY created_at, message_id"
                ).fetchall()
            else:
                rows = connection.execute(
                    "SELECT * FROM notification_outbox "
                    "WHERE status = 'PENDING' "
                    "AND (next_attempt_at IS NULL OR next_attempt_at <= ?) "
                    "ORDER BY created_at, message_id",
                    (as_of,),
                ).fetchall()
        return [dict(row) for row in rows]
    def get_message(self, signal_id):
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM notification_outbox WHERE signal_id = ?",
                (signal_id,),
            ).fetchone()
        return dict(row) if row else None

    def mark_sent(self, signal_id, sent_at):
        if not sent_at:
            raise ValueError("sent_at is required after confirmed delivery")
        with self._connect() as connection:
            cursor = connection.execute(
                "UPDATE notification_outbox "
                "SET status = 'SENT', sent_at = ?, last_error = NULL, next_attempt_at = NULL "
                "WHERE signal_id = ? AND status = 'PENDING'",
                (sent_at, signal_id),
            )
            if cursor.rowcount != 1:
                raise ValueError(f"No pending outbox message found for signal: {signal_id}")

    def mark_failed(self, signal_id, error, next_attempt_at):
        if not error or not next_attempt_at:
            raise ValueError("error and next_attempt_at are required")
        with self._connect() as connection:
            cursor = connection.execute(
                "UPDATE notification_outbox "
                "SET attempts = attempts + 1, last_error = ?, next_attempt_at = ? "
                "WHERE signal_id = ? AND status = 'PENDING'",
                (str(error), next_attempt_at, signal_id),
            )
            if cursor.rowcount != 1:
                raise ValueError(f"No pending outbox message found for signal: {signal_id}")


