import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.futures_wrapper_v2 import XTFuturesExchange

w = XTFuturesExchange(dry_run=True)

print("=== Test 1: Set leverage to 10x on fet_usdt (SHORT) ===")
ok, data = w._request(
    "POST",
    "/future/user/v1/position/adjust-leverage",
    body="symbol=fet_usdt&positionSide=SHORT&leverage=10"
)
print(f"ok={ok}")
print(json.dumps(data, indent=2)[:500])

print("\n=== Test 2: Read back leverage ===")
ok, data = w._request(
    "GET",
    "/future/trade/v1/position/leverage/list",
    query="symbol=fet_usdt"
)
print(f"ok={ok}")
print(json.dumps(data, indent=2)[:500])
