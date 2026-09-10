from exchanges.base_exchange import BaseExchange


class MockExchange(BaseExchange):
    """صرافی آزمایشی برای تست ققنوس"""

    def connect(self):
        return "Mock Exchange Connected"

    def get_price(self, symbol):

        prices = {
            "BTCUSDT": 65000,
            "ETHUSDT": 3500
        }

        return prices.get(symbol)

    def get_balance(self):

        return {
            "USDT": 1000,
            "BTC": 0.01
        }

    def get_candle(self, symbol, timeframe="1m"):

        candles = {

            "BTCUSDT": {

                "1m": {
                    "timestamp": 1752364800,
                    "open": 64950,
                    "high": 65100,
                    "low": 64800,
                    "close": 65000,
                    "volume": 125.5
                },

                "30m": {
                    "timestamp": 1752366600,
                    "open": 64800,
                    "high": 65200,
                    "low": 64750,
                    "close": 65100,
                    "volume": 850
                },

                "4H": {
                    "timestamp": 1752372000,
                    "open": 64000,
                    "high": 65500,
                    "low": 63800,
                    "close": 65000,
                    "volume": 5200
                },

                "1D": {
                    "timestamp": 1752360000,
                    "open": 63000,
                    "high": 66000,
                    "low": 62500,
                    "close": 65000,
                    "volume": 15000
                }
            },

            "ETHUSDT": {

                "1m": {
                    "timestamp": 1752364800,
                    "open": 3480,
                    "high": 3520,
                    "low": 3460,
                    "close": 3500,
                    "volume": 850
                }
            }
        }

        return candles.get(symbol, {}).get(timeframe)

    def get_historical_candles(
        self,
        symbol,
        timeframe="1m",
        limit=30
    ):

        base_prices = {
            "BTCUSDT": 65000,
            "ETHUSDT": 3500
        }

        base_price = base_prices.get(symbol)

        if base_price is None:
            return []

        current_candle = self.get_candle(symbol, timeframe)

        if current_candle is None:
            return []

        current_price = current_candle["close"]

        timeframe_seconds = {
            "1m": 60,
            "30m": 1800,
            "4H": 14400,
            "1D": 86400
        }

        interval = timeframe_seconds.get(timeframe, 60)

        current_timestamp = current_candle["timestamp"]

        candles = []

        start_price = current_price - ((limit - 1) * 200)

        for index in range(limit):

            close = start_price + (index * 200)

            open_price = close - 100
            high = close + 150
            low = close - 150
            volume = 100 + (index * 5)

            timestamp = (
                current_timestamp
                - ((limit - index) * interval)
            )

            candles.append({
                "timestamp": timestamp,
                "open": open_price,
                "high": high,
                "low": low,
                "close": close,
                "volume": volume
            })

        return candles