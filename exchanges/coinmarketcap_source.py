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

    def _extract_price(self, data, asset, quote_symbol="USD"):
        assets = data.get("data")

        if not isinstance(assets, list):
            raise ValueError("Unexpected CoinMarketCap data format")

        for item in assets:
            if not isinstance(item, dict):
                continue

            if item.get("symbol") != asset:
                continue

            quotes = item.get("quote")

            if not isinstance(quotes, list):
                raise ValueError("Unexpected CoinMarketCap quote format")

            for quote in quotes:
                if not isinstance(quote, dict):
                    continue

                if quote.get("symbol") == quote_symbol:
                    price = quote.get("price")

                    if price is None:
                        raise ValueError(
                            f"CoinMarketCap price missing for {asset}/{quote_symbol}"
                        )

                    return float(price)

            raise ValueError(
                f"CoinMarketCap quote not found for {asset}/{quote_symbol}"
            )

        raise ValueError(
            f"CoinMarketCap asset not found: {asset}"
        )

    def get_price(self, symbol):
        asset = self._normalize_symbol(symbol)

        data = self._request(
            "/v3/cryptocurrency/quotes/latest",
            {
                "symbol": asset,
                "convert": "USD"
            }
        )

        return self._extract_price(data, asset)

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

    def health_check(self):
        return True