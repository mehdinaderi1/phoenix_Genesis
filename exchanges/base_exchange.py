from abc import ABC, abstractmethod


class BaseExchange(ABC):
    """کلاس پایه تمام صرافی‌ها"""

    @abstractmethod
    def connect(self):
        pass


    @abstractmethod
    def get_price(self, symbol):
        pass


    @abstractmethod
    def get_balance(self):
        pass


    @abstractmethod
    def get_candle(self, symbol, timeframe="1m"):
        pass