import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.futures_wrapper_v2 import XTFuturesExchange

w = XTFuturesExchange(dry_run=True)
w._notify("🧪 Notification from wrapper - ready for real trades")
print("Sent. Check Telegram.")
