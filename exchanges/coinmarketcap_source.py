from urllib.parse import urlencode
import json
import urllib.request

from core.market_data.source import MarketDataSource


class CoinMarketCapSource(MarketDataSource):
    """CoinMarketCap aggregate market-data source for Phoenix Genesis."""

    BASE_URL = "https://pro-api.coinmarketcap.com"
    PUBLIC_PREFIX = "/public-api"

    SYMBOL_MAP = {
        "BTCUSDT": "BTC",
        "BTCUSD": "BTC",
        "ETHUSDT": "ETH",
        "ETHUSD": "ETH",
    }

    def __init__(self, api_key=None, timeout=10):
        self.api_key = api_key
        self.timeout = timeout
        self.connected = False

    def _request(self, path, params=None):
        url = f"{self.BASE_URL}{self.PUBLIC_PREFIX}{path}"

        if params:
            url = f"{url}?{urlencode(params)}"

        headers = {
            "User-Agent": "PhoenixGenesis/1.0",
            "Accept": "application/json",
        }

        if self.api_key:
            headers["X-CMC_PRO_API_KEY"] = self.api_key

        request = urllib.request.Request(
            url,
            headers=headers
        )

        with urllib.request.urlopen(
            request,
            timeout=self.timeout
        ) as response:
            return json.loads(response.read().decode("utf-8"))

    def connect(self):
        self._request(
            "/v3/cryptocurrency/quotes/latest",
            {"symbol": "BTC", "convert": "USD"}
        )
        self.connected = True
        return "CoinMarketCap Connected"

    def _normalize_symbol(self, symbol):
        try:
            return self.SYMBOL_MAP[symbol]
        except KeyError as exc:
            raise ValueError(
                f"Unsupported CoinMarketCap symbol: {symbol}"
            ) from exc

    def get_price(self, symbol):
        asset = self._normalize_symbol(symbol)

        data = self._request(
            "/v3/cryptocurrency/quotes/latest",
            {
                "symbol": asset,
                "convert": "USD"
            }
        )

        quote = data["data"][asset]["quote"]["USD"]
        return float(quote["price"])

    def get_candle(self, symbol, timeframe="1m"):
        raise NotImplementedError(
            "CoinMarketCap aggregate source does not provide exchange-style candles here."
        )

    def get_historical_candles(
        self,
        symbol,
        timeframe="1m",
        limit=30
    ):
        raise NotImplementedError(
            "CoinMarketCap aggregate source does not provide exchange-style historical candles here."
        )
