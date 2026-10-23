"""
SAFE ORDER TEST — BUY limit at 50% below market.
Uses existing XTExchange for price (already works).
"""
import os, sys, hmac, hashlib, time, json
import urllib.request
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from exchanges.xt_exchange import XTExchange

BASE_URL = "https://sapi.xt.com"
API_KEY = os.getenv("XT_API_KEY")
API_SECRET = os.getenv("XT_API_SECRET")

if not API_KEY or not API_SECRET:
    print("Set XT_API_KEY and XT_API_SECRET")
    sys.exit(1)


def get_server_time():
    req = urllib.request.Request(f"{BASE_URL}/v4/public/time",
        headers={"User-Agent": "PhoenixGenesis/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())["result"]["serverTime"]


OFFSET_MS = get_server_time() - int(time.time() * 1000)


def sign(method, path, query=None, body=None, recv_window=60000):
    timestamp = str(int(time.time() * 1000) + OFFSET_MS)
    h = {
        "validate-algorithms": "HmacSHA256",
        "validate-appkey": API_KEY,
        "validate-recvwindow": str(recv_window),
        "validate-timestamp": timestamp,
    }
    x = "&".join(f"{k}={v}" for k, v in sorted(h.items()))
    parts = [method, path]
    if query:
        parts.append("&".join(f"{k}={v}" for k, v in sorted(query.items())))
    if body is not None:
        parts.append(json.dumps(body, separators=(",", ":")))
    y = "#" + "#".join(parts)
    sig = hmac.new(API_SECRET.encode(), (x + y).encode(), hashlib.sha256).hexdigest()
    h["validate-signature"] = sig
    return h


def call(method, path, query=None, body=None):
    headers = sign(method, path, query=query, body=body)
    url = f"{BASE_URL}{path}"
    if query:
        url = f"{url}?" + "&".join(f"{k}={v}" for k, v in sorted(query.items()))
    data = None
    if body is not None:
        data = json.dumps(body, separators=(",", ":")).encode()
    req = urllib.request.Request(url, data=data,
        headers={**headers, "User-Agent": "PhoenixGenesis/1.0",
                 "Content-Type": "application/json"},
        method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode())


def get_current_price():
    """Use XTExchange which already works."""
    xt = XTExchange(timeout=10)
    data = xt.get_price("BTCUSDT")
    if data is None:
        raise RuntimeError("XTExchange.get_price returned None")
    # Handle both object and dict formats
    if hasattr(data, "price"):
        return float(data.price)
    if isinstance(data, dict):
        return float(data.get("price") or data.get("lastPrice") or data.get("c"))
    return float(data)


def get_available_usdt():
    resp = call("GET", "/v4/balances")
    if resp.get("rc") != 0:
        return 0
    for a in resp["result"]["assets"]:
        if a["currency"].lower() == "usdt":
            return float(a.get("availableAmount", 0))
    return 0


def main():
    print("=" * 60)
    print("SAFE ORDER TEST — BUY limit @ 50% below market")
    print("=" * 60)
    print()

    print("Fetching price via XTExchange...")
    price = get_current_price()
    print(f"  BTC/USDT = {price:,.2f}")
    print()

    usdt = get_available_usdt()
    print(f"Available USDT: {usdt:.4f}")
    print()

    test_price = round(price * 0.50, 2)
    target_cost = usdt * 0.30
    quantity = round(target_cost / test_price, 8)

    # XT min quantity for BTC is typically 0.00001, step 0.00001
    # XT min notional is $1
    if quantity < 0.00001:
        quantity = 0.00001
    if quantity * test_price < 1.0:
        quantity = round(1.0 / test_price + 0.00001, 5)

    print(f"Test order:")
    print(f"  side:     BUY")
    print(f"  type:     LIMIT")
    print(f"  symbol:   btc_usdt")
    print(f"  price:    {test_price:,.2f}  (50% below market)")
    print(f"  quantity: {quantity:.8f} BTC")
    print(f"  cost:     {quantity * test_price:,.2f} USDT")
    print()

    if quantity * test_price > usdt * 0.9:
        print(f"ERROR: cost exceeds 90% of available USDT")
        return

    body = {
        "symbol": "btc_usdt",
        "side": "BUY",
        "type": "LIMIT",
        "timeInForce": "GTC",
        "bizType": "SPOT",
        "price": str(test_price),
        "quantity": str(quantity),
    }
    print("Placing order...")
    resp = call("POST", "/v4/order", body=body)
    print(json.dumps(resp, indent=2))
    print()

    if resp.get("rc") != 0:
        print(f">>> FAILED: {resp.get('mc')}")
        return

    order_id = resp.get("result", {}).get("orderId")
    if not order_id:
        print(">>> No orderId in response")
        return
    print(f">>> ACCEPTED: orderId={order_id}")
    print()

    # Verify
    print("Verifying in open orders...")
    resp = call("GET", "/v4/open-order", query={"symbol": "btc_usdt"})
    orders = resp.get("result", {}).get("items", [])
    found = [o for o in orders if str(o.get("orderId")) == str(order_id)]
    print(f"  found: {len(found)}")
    if found:
        o = found[0]
        print(f"  state: {o.get('state')}, price: {o.get('price')}, qty: {o.get('origQty')}")
    print()

    # Cancel
    print("Cancelling...")
    resp = call("DELETE", "/v4/open-order", body={"orderIds": [order_id]})
    if resp.get("rc") == 0:
        print(">>> CANCELLED")
    else:
        print(f">>> CANCEL FAILED: {resp.get('mc')}")
        print("  MANUAL: Go to XT web → Orders → Cancel")
    print()
    print("=" * 60)
    print("If ACCEPTED + CANCELLED: place_order + cancel_order work")
    print("=" * 60)


if __name__ == "__main__":
    main()