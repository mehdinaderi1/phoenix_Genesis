import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.futures_wrapper_v2 import XTFuturesExchange

w = XTFuturesExchange(dry_run=False, extra_skip=["btc_usdt","eth_usdt"])

# Test: does XT accept clientOrderId?
w.set_leverage("fet_usdt", "LONG", 10)

body = json.dumps({
    "symbol": "fet_usdt",
    "orderSide": "BUY",
    "positionSide": "LONG",
    "orderType": "MARKET",
    "origQty": 30,
    "clientOrderId": "phoenix_auto_test1",
})
ok, data = w._request("POST", "/future/trade/v1/order/create", body=body)
print("Response:", json.dumps(data, indent=2)[:500])
# Then close immediately
if ok and data.get("returnCode") == 0:
    order_id = data.get("result")
    print(f"Order {order_id} - checking if clientOrderId accepted...")
    # Close
    w.place_order("fet_usdt", "SELL", "LONG", 30, leverage=10)
