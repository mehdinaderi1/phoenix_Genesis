import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from notifications.telegram_sender import TelegramSender

sender = TelegramSender()
print(f"token: {'SET' if sender.token else 'MISSING'}")
print(f"chat_id: {'SET' if sender.chat_id else 'MISSING'}")

result = sender.send_message("🧪 Test from Phoenix: futures infrastructure ready")
print(f"Result: {result}")
