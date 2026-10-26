from exchanges.xt_exchange import XTExchange
from datetime import datetime

ex = XTExchange(timeout=10)

def px(sym):
    p = ex.get_price(sym)
    return getattr(p, "price", p)

btc = px("BTCUSDT")
zec = px("ZECUSDT")

print(f"[{datetime.now().strftime('%H:%M:%S')}] BTC={btc}  ZEC={zec}")

# ذخیره برای مقایسه بعدی
import json, os
snap = "data/beta_snapshot.json"
os.makedirs("data", exist_ok=True)
json.dump({"time": datetime.now().isoformat(), "btc": btc, "zec": zec}, open(snap, "w"))
print(f"saved to {snap}")
