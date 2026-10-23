"""
XT Private Exchange Adapter — authenticated trading operations.
Verified endpoints:
- GET  /v4/balances       -> fetch_balances()
- POST /v4/order          -> place_order()
- DELETE /v4/open-order   -> cancel_order()
- GET  /v4/open-order     -> get_open_orders()
"""
import os
import time
import hmac
import hashlib
import json
import urllib.request
import urllib.error
from typing import Optional, List, Dict, Any

class XTPrivateExchange:
    BASE_URL = "https://sapi.xt.com"

    def __init__(self, api_key: str = None, api_secret: str = None, timeout: int = 15):
        self.api_key = api_key or os.getenv("XT_API_KEY")
        self.api_secret = api_secret or os.getenv("XT_API_SECRET")
        self.timeout = timeout
        
        if not self.api_key or not self.api_secret:
            raise ValueError("XT_API_KEY and XT_API_SECRET must be set.")
        
        # Fetch server time offset on init
        self._time_offset_ms = self._fetch_server_time() - int(time.time() * 1000)

    def _fetch_server_time(self) -> int:
        url = f"{self.BASE_URL}/v4/public/time"
        req = urllib.request.Request(url, headers={"User-Agent": "PhoenixGenesis/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode())
                return int(data["result"]["serverTime"])
        except Exception:
            return int(time.time() * 1000)

    def _sign(self, method: str, path: str, query: dict = None, body: dict = None, recv_window: int = 60000) -> dict:
        timestamp = str(int(time.time() * 1000) + self._time_offset_ms)
        headers = {
            "validate-algorithms": "HmacSHA256",
            "validate-appkey": self.api_key,
            "validate-recvwindow": str(recv_window),
            "validate-timestamp": timestamp,
        }
        # X: sorted header string
        x = "&".join(f"{k}={v}" for k, v in sorted(headers.items()))
        
        # Y: #method#path#query#body
        parts = [method, path]
        if query:
            parts.append("&".join(f"{k}={v}" for k, v in sorted(query.items())))
        if body is not None:
            parts.append(json.dumps(body, separators=(",", ":")))
        y = "#" + "#".join(parts)
        
        sig = hmac.new(self.api_secret.encode(), (x + y).encode(), hashlib.sha256).hexdigest()
        headers["validate-signature"] = sig
        return headers

    def _request(self, method: str, path: str, query: dict = None, body: dict = None) -> dict:
        headers = self._sign(method, path, query, body)
        headers["User-Agent"] = "PhoenixGenesis/1.0"
        if body is not None:
            headers["Content-Type"] = "application/json"
        
        url = f"{self.BASE_URL}{path}"
        if query:
            url = f"{url}?" + "&".join(f"{k}={v}" for k, v in sorted(query.items()))
            
        data = json.dumps(body, separators=(",", ":")).encode() if body is not None else None
        
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                res = json.loads(resp.read().decode())
                if res.get("rc") != 0:
                    raise RuntimeError(f"XT API Error: {res.get('mc')} (rc={res.get('rc')})")
                return res
        except urllib.error.HTTPError as e:
            err_body = e.read().decode()
            try:
                err_data = json.loads(err_body)
                raise RuntimeError(f"XT HTTP Error: {err_data.get('mc')} (rc={err_data.get('rc')})")
            except json.JSONDecodeError:
                raise RuntimeError(f"XT HTTP Error {e.code}: {err_body}")

    def fetch_balances(self) -> List[dict]:
        """Get account balances."""
        res = self._request("GET", "/v4/balances")
        return res.get("result", {}).get("assets", [])

    def place_order(self, symbol: str, side: str, price: str, quantity: str, order_type: str = "LIMIT") -> str:
        """Place a spot order. Returns orderId."""
        body = {
            "symbol": symbol,
            "side": side.upper(),
            "type": order_type.upper(),
            "timeInForce": "GTC",
            "bizType": "SPOT",
            "price": str(price),
            "quantity": str(quantity)
        }
        res = self._request("POST", "/v4/order", body=body)
        return str(res["result"]["orderId"])

    def cancel_order(self, order_ids: List[str]) -> bool:
        """Cancel one or more orders."""
        body = {"orderIds": [str(oid) for oid in order_ids]}
        res = self._request("DELETE", "/v4/open-order", body=body)
        return res.get("result") is True

    def get_open_orders(self, symbol: str = None) -> List[dict]:
        """List all open orders (optionally filter by symbol)."""
        query = {"symbol": symbol} if symbol else None
        res = self._request("GET", "/v4/open-order", query=query)
        result = res.get("result")
        if isinstance(result, list):
            return result
        elif isinstance(result, dict):
            return result.get("items", [])
        return []

    def get_order(self, order_id: str) -> dict:
        """Fetch single order details. Returns empty dict if not found."""
        try:
            res = self._request("GET", f"/v4/order/{order_id}")
            return res.get("result") or {}
        except RuntimeError as e:
            if "not found" in str(e).lower() or "404" in str(e):
                return {}
            raise

    def get_history_orders(
        self, symbol: str = None, order_ids: list = None, limit: int = 50
    ) -> list:
        """Fetch historical (filled/cancelled) orders."""
        query = {"limit": str(limit)}
        if symbol:
            query["symbol"] = symbol
        if order_ids:
            query["orderIds"] = ",".join(str(x) for x in order_ids)
        try:
            res = self._request("GET", "/v4/history-order", query=query)
            result = res.get("result")
            if isinstance(result, list):
                return result
            elif isinstance(result, dict):
                return result.get("items", [])
            return []
        except RuntimeError:
            return []