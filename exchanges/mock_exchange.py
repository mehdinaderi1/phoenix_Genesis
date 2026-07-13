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
                "timestamp": 1752364800,
                "open": 64950,
                "high": 65100,
                "low": 64800,
                "close": 65000,
                "volume": 125.5
            },

            "ETHUSDT": {
                "timestamp": 1752364800,
                "open": 3480,
                "high": 3520,
                "low": 3460,
                "close": 3500,
                "volume": 850
            }
        }

        return candles.get(symbol)