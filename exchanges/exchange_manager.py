class ExchangeManager:
    """مدیر ارتباط با صرافی‌ها"""

    def __init__(self):
        self.exchange = None

    def set_exchange(self, exchange):
        self.exchange = exchange

    def connect(self):
        if self.exchange is None:
            raise ValueError("No exchange selected.")

        return self.exchange.connect()

    def get_price(self, symbol):
        if self.exchange is None:
            raise ValueError("No exchange selected.")

        return self.exchange.get_price(symbol)

    def get_balance(self):
        if self.exchange is None:
            raise ValueError("No exchange selected.")

        return self.exchange.get_balance()

    def get_candle(self, symbol):
        return self.exchange.get_candle(symbol)