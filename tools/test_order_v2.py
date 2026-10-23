"""
SAFE ORDER TEST v2 — precision-correct.
- price: 2 decimals max
- quantity: 5 decimals max
- min notional: 5 USDT (XT requirement for btc_usdt)
- Order placed 50% below market -> won't fill
- Verifies + cancels immediately
"""
import os, sys, hmac, hashlib, time, json, math
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
    xt = XTExchange(timeout=10)
    data = xt.get_price("BTCUSDT")
    if data is None:
        raise RuntimeError("XTExchange.get_price returned None")
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


def get_symbol_limits():
    """Try to fetch symbol info. Fallback to hardcoded defaults."""
    try:
        resp = call("GET", "/v4/public/symbol", query={"symbol": "btc_usdt"})
        if resp.get("rc") == 0 and resp.get("result"):
            return resp["result"]
    except Exception:
        pass
    # XT defaults for btc_usdt spot (observed)
    return {
        "pricePrecision": 2,
        "quantityPrecision": 5,
        "minNotional": 5.0,
    }


def main():
    print("=" * 60)
    print("SAFE ORDER TEST v2")
    print("=" * 60)
    print()

    price = get_current_price()
    usdt = get_available_usdt()
    print(f"Current BTC/USDT: {price:,.2f}")
    print(f"Available USDT:   {usdt:.4f}")
    print()

    limits = get_symbol_limits()
    price_prec = limits.get("pricePrecision", 2)
    qty_prec = limits.get("quantityPrecision", 5)
    min_notional = limits.get("minNotional", 5.0)
    print(f"Symbol limits:")
    print(f"  pricePrecision:    {price_prec}")
    print(f"  quantityPrecision: {qty_prec}")
    print(f"  minNotional:       {min_notional} USDT")
    print()

    if usdt < min_notional:
        print(f"ERROR: USDT ({usdt:.2f}) < minNotional ({min_notional})")
        print(">>> Deposit more USDT or use different pair.")
        return

    # Order at 50% below market (won't fill)
    raw_price = price * 0.50
    test_price = round(raw_price, price_prec)

    # Quantity: ensure notional >= minNotional * 1.1 (safety)
    target_notional = min_notional * 1.1
    raw_qty = target_notional / test_price
    quantity = round(raw_qty, qty_prec)

    # Round up if below minNotional due to rounding
    while quantity * test_price < min_notional:
        quantity = round(quantity + 10 ** (-qty_prec), qty_prec)

    notional = quantity * test_price

    print(f"Test order:")
    print(f"  symbol:   btc_usdt")
    print(f"  side:     BUY")
    print(f"  type:     LIMIT")
    print(f"  price:    {test_price:.{price_prec}f}  (50% below market)")
    print(f"  quantity: {quantity:.{qty_prec}f} BTC")
    print(f"  notional: {notional:.2f} USDT (min {min_notional})")
    print()

    if notional > usdt * 0.95:
        print(f"ERROR: notional {notional:.2f} > 95% of available {usdt:.2f}")
        return

    body = {
        "symbol": "btc_usdt",
        "side": "BUY",
        "type": "LIMIT",
        "timeInForce": "GTC",
        "bizType": "SPOT",
        "price": f"{test_price:.{price_prec}f}",
        "quantity": f"{quantity:.{qty_prec}f}",
    }
    print("Placing order...")
    resp = call("POST", "/v4/order", body=body)
    print(json.dumps(resp, indent=2))
    print()

    if resp.get("rc") != 0:
        print(f">>> FAILED: {resp.get('mc')}")
        code = resp.get("mc", "")
        if code == "ORDER_008":
            print("  -> Precision still wrong. Check pricePrecision/quantityPrecision.")
        elif code == "ORDER_002":
            print("  -> Insufficient balance. Deposit more USDT.")
        elif code == "ORDER_001":
            print("  -> Min notional still violated. Increase quantity.")
        return

    order_id = resp.get("result", {}).get("orderId")
    if not order_id:
        print(">>> No orderId in response")
        return
    print(f">>> ACCEPTED: orderId={order_id}")
    print()

    # Verify in open orders
    print("Verifying in open orders...")
    resp = call("GET", "/v4/open-order", query={"symbol": "btc_usdt"})
    orders = resp.get("result", {}).get("items", [])
    found = [o for o in orders if str(o.get("orderId")) == str(order_id)]
    print(f"  found: {len(found)}")
    if found:
        o = found[0]
        print(f"  state: {o.get('state')}")
        print(f"  price: {o.get('price')}")
        print(f"  qty:   {o.get('origQty')}")
    print()

    # Cancel
    print("Cancelling...")
    resp = call("DELETE", "/v4/open-order", body={"orderIds": [order_id]})
    if resp.get("rc") == 0:
        print(">>> CANCELLED")
    else:
        print(f">>> CANCEL FAILED: {resp.get('mc')}")
        print(f"  MANUAL: XT web -> Orders -> Cancel order {order_id}")
    print()
    print("=" * 60)
    print("If ACCEPTED + CANCELLED: full pipeline works")
    print("=" * 60)


if __name__ == "__main__":
    main()