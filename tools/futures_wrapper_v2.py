"""
XTFuturesExchange v2 - Complete wrapper with real balance, contractSize,
Hedge Mode support, and DRY_RUN protection.
"""
import os, time, hmac, hashlib, json, urllib.request, urllib.error


class XTFuturesExchange:
    BASE_URL = "https://fapi.xt.com"

    def __init__(self, dry_run=True, extra_skip=None):
        self.api_key = os.environ.get("XT_API_KEY", "")
        self.api_secret = os.environ.get("XT_API_SECRET", "")
        self.dry_run = dry_run
        # NEVER touch these (user's manual positions)
        self.skip_symbols = ["btc_usdt"]
        if extra_skip:
            self.skip_symbols.extend([s.lower() for s in extra_skip])
        if not self.api_key or not self.api_secret:
            raise ValueError("XT_API_KEY and XT_API_SECRET must be set")
        self._contract_cache = {}
        self._last_request_time = 0
        self._min_interval = 0.25  # حداقل ۲۵۰ms بین درخواست‌ها

        # Telegram notifier (optional, uses existing notifications module)
        self.notifier = None
        try:
            if os.environ.get("TELEGRAM_ENABLED") == "1" or os.environ.get("PHOENIX_TELEGRAM_ENABLED") == "1":
                from notifications.telegram_sender import TelegramSender
                self.notifier = TelegramSender()
                print("[Wrapper] Telegram notifier ready")
        except Exception as e:
            print(f"[Wrapper] Telegram disabled: {e}")

    def _sign(self, method, path, query="", body=""):
        ts = str(int(time.time() * 1000))
        fixed = f"validate-appkey={self.api_key}&validate-timestamp={ts}"
        unenc = f"{fixed}#{path}#{query}" if query else (f"{fixed}#{path}#{body}" if body else f"{fixed}#{path}")
        return ts, hmac.new(self.api_secret.encode(), unenc.encode(), hashlib.sha256).hexdigest()

    def _request(self, method, path, query="", body="", content_type="application/json"):
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        self._last_request_time = time.time()

        ts, sig = self._sign(method, path, query, body)
        url = self.BASE_URL + path + ("?" + query if query else "")

        last_error = None
        for attempt in range(2):
            req = urllib.request.Request(url, method=method)
            req.add_header("validate-appkey", self.api_key)
            req.add_header("validate-timestamp", ts)
            req.add_header("validate-signature", sig)
            req.add_header("validate-algorithms", "HmacSHA256")
            req.add_header("validate-recvwindow", "10000")
            req.add_header("Content-Type", content_type)   # ← از پارامتر
            if body:
                req.data = body.encode()
            try:
                with urllib.request.urlopen(req, timeout=15) as r:
                    return True, json.loads(r.read().decode())
            except urllib.error.HTTPError as e:
                last_error = json.loads(e.read().decode())
                if e.code < 500:
                    return False, last_error
                time.sleep(1)
            except Exception as e:
                last_error = {"error": str(e)}
                time.sleep(1)
        return False, last_error

    def get_balance(self):
        """Return balance with retry on transient failures."""
        for attempt in range(3):
            ok, data = self._request("GET", "/future/user/v1/compat/balance/list")
            if ok and isinstance(data, dict):
                for asset in data.get("result", []):
                    if asset.get("coin", "").lower() == "usdt":
                        return {
                            "available": float(asset.get("amount", 0)),
                            "equity": float(asset.get("walletBalance", 0)),
                            "margin_used": float(asset.get("crossedMargin", 0)) + float(asset.get("isolatedMargin", 0)),
                            "profit": float(asset.get("profit", 0)),
                            "not_profit": float(asset.get("notProfit", 0)),
                        }
            if attempt < 2:
                time.sleep(1)
        return None

    def get_contract_size(self, symbol):
        sym_lower = symbol.lower()
        if sym_lower in self._contract_cache:
            return self._contract_cache[sym_lower]
        ok, data = self._request("GET", "/future/market/v1/public/symbol/detail", f"symbol={sym_lower}")
        if not ok:
            return None
        size = float(data.get("result", {}).get("contractSize", 0))
        self._contract_cache[sym_lower] = size
        return size

    def _get_price(self, symbol):
        """Get last price from ticker endpoint."""
        sym = symbol.lower()
        ok, data = self._request("GET", "/future/market/v1/public/q/ticker", f"symbol={sym}")
        if ok:
            result = data.get("result")
            if isinstance(result, list) and result:
                result = result[0]
            if isinstance(result, dict):
                # XT ticker fields: c=close, h=high, l=low, o=open
                for key in ("c", "lastPrice", "last_price", "price", "markPrice", "mark_price", "close"):
                    if key in result and result[key]:
                        try:
                            return float(result[key])
                        except (ValueError, TypeError):
                            continue
        return None

    def get_positions(self, include_skipped=False):
        ok, data = self._request("GET", "/future/user/v1/position/list")
        if not ok:
            return False, data
        if not include_skipped:
            if isinstance(data.get("result"), list):
                data["result"] = [p for p in data["result"] if p.get("symbol", "").lower() not in self.skip_symbols]
        return True, data

    def get_user_positions(self):
        """Return all positions including protected ones."""
        ok, data = self._request("GET", "/future/user/v1/position/list")
        if not ok:
            return []
        return data.get("result", []) or []

    def get_user_btc_position(self):
        for p in self.get_user_positions():
            if p.get("symbol", "").lower() == "btc_usdt":
                return p
        return None

    def calculate_contracts(self, symbol, risk_pct=1.0, leverage=30, price=None):
        balance = self.get_balance()
        if not balance or balance["available"] <= 0:
            return {"error": "no balance or available=0"}
        margin = balance["available"] * (risk_pct / 100.0)
        notional = margin * leverage
        if price is None:
            price = self._get_price(symbol)
            if price is None:
                return {"error": "cannot get price"}
        csize = self.get_contract_size(symbol)
        if not csize:
            return {"error": "cannot get contractSize"}
        contracts = int(notional / (price * csize))
        return {
            "margin_usdt": round(margin, 2),
            "notional_usdt": round(notional, 2),
            "contracts": contracts,
            "price": price,
            "contract_size": csize,
        }

    def set_leverage(self, symbol, position_side, leverage):
        """Set leverage for a symbol + position side before placing orders."""
        sym = symbol.lower()
        body = f"symbol={sym}&positionSide={position_side}&leverage={leverage}"
        ok, data = self._request(
            "POST",
            "/future/user/v1/position/adjust-leverage",
            body=body,
            content_type="application/x-www-form-urlencoded",
        )
        success = ok and (isinstance(data, dict) and data.get("returnCode") == 0)
        return success, data

    def get_leverage(self, symbol, position_side=None):
        """Read current leverage for a symbol."""
        ok, data = self._request(
            "GET",
            "/future/trade/v1/position/leverage/list",
            query=f"symbol={symbol.lower()}",
        )
        if not ok:
            return None
        for item in data.get("result", []) or []:
            if position_side is None or item.get("positionSide") == position_side:
                return item.get("leverage")
        return None

    def _notify(self, message):
        """Send Telegram notification (silent if disabled)."""
        if self.notifier is None:
            return
        try:
            self.notifier.send_message(message)
        except Exception as e:
            print(f"[Telegram] send failed: {e}")

    def place_order(self, symbol, side, position_side, contracts, leverage=10,
                sl_price=None, tp_price=None, order_type="MARKET", price=None):
        sym_lower = symbol.lower()
        if sym_lower in self.skip_symbols:
            return False, {"error": f"SKIP: {sym_lower} is protected (user's manual position)"}

        # ساخت بدنه سفارش طبق مستندات XT
        order = {
            "symbol": sym_lower,
            "orderSide": side,
            "positionSide": position_side,
            "orderType": order_type,   # ← تغییر از type به orderType
            "origQty": contracts,
        }

        # تنظیمات مربوط به سفارش LIMIT
        if order_type == "LIMIT" and price:
            order["price"] = price
            order["timeInForce"] = "GTC"

        # SL/TP اختیاری (طبق مستندات، این فیلدها در همین endpoint پشتیبانی می‌شوند)
        if sl_price:
            order["triggerStopPrice"] = sl_price
            order["triggerStopType"] = "MARK_PRICE"
        if tp_price:
            order["triggerProfitPrice"] = tp_price
            order["triggerProfitType"] = "MARK_PRICE"

        # Set leverage before order
        lev_ok, lev_resp = self.set_leverage(symbol, position_side, leverage)
        if not lev_ok:
            return False, {"error": "leverage_set_failed", "response": lev_resp}

        # حالت DRY_RUN
        if self.dry_run:
            return True, {"dry_run": True, "would_send": order, "note": "DRY_RUN=1"}

        # ارسال درخواست
        body = json.dumps(order)
        ok, data = self._request("POST", "/future/trade/v1/order/create", body=body)
        if ok and isinstance(data, dict) and data.get("returnCode") == 0:
            self._notify(
                f"🟢 {position_side} OPEN\n"
                f"Symbol: {sym_lower.upper()}\n"
                f"Size: {contracts} contracts @ {leverage}x\n"
                f"Order ID: {data.get('result')}"
            )
        return ok, data

    def health_check(self):
        balance = self.get_balance()
        if not balance:
            return {"healthy": False, "error": "balance fetch failed"}
        positions = self.get_user_positions()
        return {
            "healthy": True,
            "dry_run": self.dry_run,
            "balance": balance,
            "skip_symbols": self.skip_symbols,
            "active_positions": [
                {"symbol": p.get("symbol"), "side": p.get("positionSide"),
                 "size": p.get("positionSize")}
                for p in positions
            ],
        }


if __name__ == "__main__":
    import sys
    print("=" * 70)
    print("XT Futures Wrapper v2.1 - Fixed")
    print("=" * 70)

    # Optional: pass extra skip symbols as args
    extra = sys.argv[1:] if len(sys.argv) > 1 else None
    if extra:
        print(f"Extra skip symbols: {extra}")

    wrapper = XTFuturesExchange(dry_run=True, extra_skip=extra)

    health = wrapper.health_check()
    print(f"\n[HEALTH]")
    print(json.dumps(health, indent=2))

    print("\n[PRICE TEST]")
    for sym in ["fet_usdt", "bnb_usdt", "xrp_usdt"]:
        p = wrapper._get_price(sym)
        cs = wrapper.get_contract_size(sym)
        print(f"  {sym}: price={p}, contract_size={cs}")

    print("\n[SIZING TEST - FET]")
    for lev in [10, 30]:
        s = wrapper.calculate_contracts("fet_usdt", risk_pct=1.0, leverage=lev)
        print(f"  Leverage {lev}x: {s}")

    print("\n[SIZING TEST - BNB]")
    for lev in [10, 30]:
        s = wrapper.calculate_contracts("bnb_usdt", risk_pct=1.0, leverage=lev)
        print(f"  Leverage {lev}x: {s}")

    print("\n[DRY_RUN ORDER - FET SHORT]")
    sizing = wrapper.calculate_contracts("fet_usdt", risk_pct=1.0, leverage=30)
    if "contracts" in sizing and sizing["contracts"] > 0:
        ok, result = wrapper.place_order(
            symbol="fet_usdt",
            side="SELL",
            position_side="SHORT",
            contracts=sizing["contracts"],
            leverage=30,
            sl_price=round(sizing["price"] * 1.01, 6),
            tp_price=round(sizing["price"] * 0.98, 6),
        )
        print(f"  Result: {json.dumps(result, indent=2)}")

    print("\n[DRY_RUN ORDER - BTC (should be BLOCKED)]")
    ok, result = wrapper.place_order("btc_usdt", "SELL", "SHORT", 10, leverage=30)
    print(f"  Result: {result}")

    print("\n" + "=" * 70)
