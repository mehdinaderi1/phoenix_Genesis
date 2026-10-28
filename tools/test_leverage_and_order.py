import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.futures_wrapper_v2 import XTFuturesExchange

w = XTFuturesExchange(dry_run=True, extra_skip=["btc_usdt", "eth_usdt"])

print("=== DRY_RUN: place_order with leverage 30 ===")
ok, resp = w.place_order(
    symbol="fet_usdt",
    side="SELL",
    position_side="SHORT",
    contracts=30,
    leverage=30,
)
print(f"ok={ok}")
print(json.dumps(resp, indent=2)[:400])

print("\n=== Verify leverage was set to 30 ===")
lev = w.get_leverage("fet_usdt", "SHORT")
print(f"leverage = {lev}")

print("\n=== Reset back to 10 (safety) ===")
w.set_leverage("fet_usdt", "SHORT", 10)
print(f"leverage now = {w.get_leverage('fet_usdt', 'SHORT')}")
