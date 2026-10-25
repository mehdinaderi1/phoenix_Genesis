from urllib.parse import urlencode
import json
import time
import urllib.request

from exchanges.base_exchange import BaseExchange


class XTExchange(BaseExchange):
    """Public XT market-data adapter for Phoenix Genesis."""

    BASE_URL = "https://sapi.xt.com"

    TIMEFRAME_MAP = {
        "1m": "1m",
        "5m": "5m",
        "15m": "15m",
        "30m": "30m",
	"1H": "1h",
        "4H": "4h",
        "1D": "1d",
    }

    def __init__(self, timeout=3):
        self.timeout = timeout
        self.connected = False

    def _request(self, path, params=None):
        url = f"{self.BASE_URL}{path}"

        if params:
            url = f"{url}?{urlencode(params)}"

        request = urllib.request.Request(
            url,
            headers={"User-Agent": "PhoenixGenesis/1.0"}
        )

        last_error = None

        for attempt in range(3):
            try:
                with urllib.request.urlopen(
                    request,
                    timeout=self.timeout
                ) as response:
                    return json.loads(response.read().decode("utf-8"))
            except OSError as exc:
                last_error = exc
                if attempt == 2:
                    raise
                time.sleep(2 ** attempt)

        raise last_error
    def connect(self):
        self._request(
            "/v4/public/ticker/price",
            {"symbol": "btc_usdt"}
        )
        self.connected = True
        return "XT Connected"

    def get_price(self, symbol):
        xt_symbol = symbol.lower().replace("usdt", "_usdt")

        data = self._request(
            "/v4/public/ticker/price",
            {"symbol": xt_symbol}
        )

        result = data.get("result")
        if not result:
            return None

        return float(result[0]["p"])

    def get_balance(self):
        raise NotImplementedError(
            "XT public adapter does not provide account balance."
        )

    def _normalize_interval(self, timeframe):
        try:
            return self.TIMEFRAME_MAP[timeframe]
        except KeyError as exc:
            raise ValueError(
                f"Unsupported XT timeframe: {timeframe}"
            ) from exc

    def _candle_from_xt(self, candle):
        return {
            "timestamp": int(candle["t"] / 1000),
            "open": float(candle["o"]),
            "high": float(candle["h"]),
            "low": float(candle["l"]),
            "close": float(candle["c"]),
            "volume": float(candle["v"]),
        }

    def get_candle(self, symbol, timeframe="1m"):
        interval = self._normalize_interval(timeframe)
        xt_symbol = symbol.lower().replace("usdt", "_usdt")

        data = self._request(
            "/v4/public/kline",
            {
                "symbol": xt_symbol,
                "interval": interval,
                "limit": 1,
            }
        )

        result = data.get("result")
        if not result:
            return None

        return self._candle_from_xt(result[0])

    def get_historical_candles(
        self,
        symbol,
        timeframe="1m",
        limit=30
    ):
        interval = self._normalize_interval(timeframe)

        if limit <= 0:
            return []

        xt_symbol = symbol.lower().replace("usdt", "_usdt")

        data = self._request(
            "/v4/public/kline",
            {
                "symbol": xt_symbol,
                "interval": interval,
                "limit": limit,
            }
        )

        result = data.get("result") or []

        result = sorted(
            result,
            key=lambda candle: candle["t"]
        )

        return [
            self._candle_from_xt(candle)
            for candle in result
        ]

    def health_check(self):
        try:
            self.get_price("BTCUSDT")
            return True
        except Exception:
            return False
