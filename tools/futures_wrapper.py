"""
XTFuturesExchange - wrapper for XT Futures API.
SAFETY: Never touches btc_usdt position (user's manual trade).
Always in DRY_RUN mode until explicitly enabled.
"""
import os, time, hmac, hashlib, json, urllib.request, urllib.error


class XTFuturesExchange:
    BASE_URL = "https://fapi.xt.com"

    def __init__(self, dry_run=True):
        self.api_key = os.environ.get("XT_API_KEY", "")
        self.api_secret = os.environ.get("XT_API_SECRET", "")
        self.dry_run = dry_run
        self.balance_usdt = float(os.environ.get("XT_FUTURES_BALANCE_USDT", "0") or 0)
        # NEVER touch these symbols (user's manual positions)
        self.skip_symbols = ["btc_usdt"]
        if not self.api_key or not self.api_secret:
            raise ValueError("XT_API_KEY and XT_API_SECRET must be set")

    def _sign(self, method, path, query=""):
        ts = str(int(time.time() * 1000))
        fixed = f"validate-appkey={self.api_key}&validate-timestamp={ts}"
        unenc = f"{fixed}#{path}#{query}" if query else f"{fixed}#{path}"
        return ts, hmac.new(self.api_secret.encode(), unenc.encode(), hashlib.sha256).hexdigest()

    def _request(self, method, path, query="", body=""):
        ts, sig = self._sign(method, path, query)
        url = self.BASE_URL + path + ("?" + query if query else "")
        req = urllib.request.Request(url, method=method)
        req.add_header("validate-appkey", self.api_key)
        req.add_header("validate-timestamp", ts)
        req.add_header("validate-signature", sig)
        req.add_header("validate-algorithms", "HmacSHA256")
        req.add_header("validate-recvwindow", "10000")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        if body:
            req.data = body.encode()
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                return True, json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            return False, json.loads(e.read().decode())
        except Exception as e:
            return False, {"error": str(e)}

    def get_account_info(self):
        return self._request("GET", "/future/user/v1/account/info")

    def get_positions(self, include_user_positions=False):
        """Return all positions. By default, filter out user's manual symbols."""
        ok, data = self._request("GET", "/future/user/v1/position/list")
        if not ok:
            return False, data
        if not include_user_positions:
            if isinstance(data.get("result"), list):
                data["result"] = [
                    p for p in data["result"]
                    if p.get("symbol", "").lower() not in self.skip_symbols
                ]
        return True, data

    def get_user_btc_position(self):
        """Read BTC position separately (read-only, never modify)."""
        ok, data = self._request("GET", "/future/user/v1/position/list")
        if not ok:
            return None
        if isinstance(data.get("result"), list):
            for p in data["result"]:
                if p.get("symbol", "").lower() == "btc_usdt":
                    return p
        return None

    def calculate_position_size(self, risk_pct=1.0, leverage=30):
        """
        Calculate position size in USDT margin.
        risk_pct = percent of balance to risk per trade (default 1%)
        Returns (margin_usdt, notional_usdt)
        """
        if self.balance_usdt <= 0:
            return 0, 0
        margin = self.balance_usdt * (risk_pct / 100.0)
        notional = margin * leverage
        return round(margin, 4), round(notional, 2)

    def place_order(self, symbol, side, size, order_type="MARKET", price=None, leverage=10):
        """
        Place order. side = 'BUY' or 'SELL'.
        In dry_run mode: log only, no real order.
        NEVER place order on skip_symbols.
        """
        sym_lower = symbol.lower()
        if sym_lower in self.skip_symbols:
            return False, {"error": f"SKIP: {sym_lower} is in skip_symbols (user's manual position)"}

        if self.dry_run:
            return True, {
                "dry_run": True,
                "would_place": {
                    "symbol": sym_lower, "side": side, "size": size,
                    "type": order_type, "leverage": leverage,
                },
                "note": "DRY_RUN=1, no real order sent",
            }

        # Real order would go here
        # Placeholder for tomorrow
        return False, {"error": "Real order placement not yet implemented"}

    def health_check(self):
        """Quick check that auth works."""
        ok, data = self.get_account_info()
        if not ok:
            return {"healthy": False, "error": data}
        result = data.get("result", {})
        return {
            "healthy": True,
            "account_id": result.get("accountId"),
            "allow_trade": result.get("allowTrade"),
            "allow_open_position": result.get("allowOpenPosition"),
            "skip_symbols": self.skip_symbols,
            "dry_run": self.dry_run,
            "balance_usdt": self.balance_usdt,
        }


if __name__ == "__main__":
    print("=" * 60)
    print("XT Futures Wrapper - Health Check")
    print("=" * 60)

    wrapper = XTFuturesExchange(dry_run=True)

    health = wrapper.health_check()
    print(f"Health: {health}")

    print("\n--- Positions (excluding user's BTC) ---")
    ok, data = wrapper.get_positions()
    if ok:
        result = data.get("result", []) or []
        print(f"Total non-BTC positions: {len(result)}")
        for p in result:
            print(f"  {p.get('symbol')}: {p.get('positionSide')} size={p.get('positionSize')} entry={p.get('entryPrice')}")

    print("\n--- User's BTC position (read-only) ---")
    btc = wrapper.get_user_btc_position()
    if btc:
        print(f"  BTC: {btc.get('positionSide')} size={btc.get('positionSize')} entry={btc.get('entryPrice')}")
    else:
        print("  No BTC position")

    print("\n--- Position sizing test (balance-based) ---")
    margin, notional = wrapper.calculate_position_size(risk_pct=1.0, leverage=30)
    print(f"  Balance: ${wrapper.balance_usdt}")
    print(f"  Risk 1%: ${margin} margin")
    print(f"  Leverage 30x: ${notional} notional")

    print("\n--- DRY_RUN test ---")
    ok, data = wrapper.place_order("fet_usdt", "SELL", 10, leverage=10)
    print(f"Place order result: {data}")
