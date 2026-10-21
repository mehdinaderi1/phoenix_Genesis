# test_dispatch.py
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
loaded = load_dotenv(dotenv_path=env_path, override=True)
token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")

print(f"env_path: {env_path} (exists={env_path.exists()})")
print(f"loaded: {loaded}")
print(f"token: {'OK (' + str(len(token)) + ' chars)' if token else 'MISSING'}")
print(f"chat_id: {chat_id or 'MISSING'}")

if not token or not chat_id:
    raise SystemExit("token/chat_id missing")

# ۱. مستقیم به DB اضافه کن
from notifications.signal_outbox import SignalOutbox
from notifications.signal_publisher import SignalPublisher
from intelligence.action_proposal import ActionProposal
from types import SimpleNamespace

outbox = SignalOutbox("data/phoenix_notifications.db")
publisher = SignalPublisher(outbox, primary_timeframe="5m")

proposal = ActionProposal(action="BUY", status="APPROVED", reason="manual dispatch test", confidence=75)
obs = SimpleNamespace(symbol="BTCUSDT", price=83000.0, timestamp="2026-10-21T16:00:00Z")
boundaries = {"5m": {"candle_start": "1792509000"}}

result = publisher.publish(proposal, obs, boundaries, generated_at="2026-10-21T16:00:00Z")
print(f"publish: {'created' if result else 'duplicate/None'}")

# ۲. چک pending
import sqlite3
conn = sqlite3.connect("data/phoenix_notifications.db")
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM notification_outbox WHERE sent_at IS NULL")
print(f"pending: {cur.fetchone()[0]}")
conn.close()

# ۳. dispatcher
from notifications.dispatcher import NotificationDispatcher
from notifications.telegram_sender import TelegramSender

dispatcher = NotificationDispatcher(outbox=outbox, sender=TelegramSender())
print(f"dispatch: {dispatcher.dispatch_due_messages()}")
