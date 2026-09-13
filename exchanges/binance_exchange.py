from urllib.parse import urlencode
import json
import urllib.request

from exchanges.base_exchange import BaseExchange


class BinanceExchange(BaseExchange):
    """Public Binance market-data adapter for Phoenix Genesis."""

    BASE_URL = "https://api.binance.com"

    TIMEFRAME_MAP = {
        "1m": "1m",
        "30m": "30m",
        "4H": "4h",
        "1D": "1d",
    }

    def __init__(self, timeout=10):
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

        with urllib.request.urlopen(
            request,
            timeout=self.timeout
        ) as response:
            return json.loads(response.read().decode("utf-8"))

    def connect(self):
        self._request("/api/v3/ping")
        self.connected = True
        return "Binance Connected"

    def get_price(self, symbol):
        data = self._request(
            "/api/v3/ticker/price",
            {"symbol": symbol}
        )

        return float(data["price"])

    def get_balance(self):
        raise NotImplementedError(
            "Binance public adapter does not provide account balance."
        )

    def _normalize_interval(self, timeframe):
        try:
            return self.TIMEFRAME_MAP[timeframe]
        except KeyError as exc:
            raise ValueError(
                f"Unsupported Binance timeframe: {timeframe}"
            ) from exc

    def _candle_from_binance(self, candle):
        return {
            "timestamp": int(candle[0] / 1000),
            "open": float(candle[1]),
            "high": float(candle[2]),
            "low": float(candle[3]),
            "close": float(candle[4]),
            "volume": float(candle[5]),
        }

    def get_candle(self, symbol, timeframe="1m"):
        interval = self._normalize_interval(timeframe)

        data = self._request(
            "/api/v3/klines",
            {
                "symbol": symbol,
                "interval": interval,
                "limit": 1
            }
        )

        if not data:
            return None

        return self._candle_from_binance(data[0])

    def get_historical_candles(
        self,
        symbol,
        timeframe="1m",
        limit=30
    ):
        interval = self._normalize_interval(timeframe)

        if limit <= 0:
            return []

        data = self._request(
            "/api/v3/klines",
            {
                "symbol": symbol,
                "interval": interval,
                "limit": limit
            }
        )

        return [
            self._candle_from_binance(candle)
            for candle in data
        ]
