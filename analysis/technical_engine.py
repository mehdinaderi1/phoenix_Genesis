from analysis.indicators.moving_average import MovingAverage
from analysis.indicators.rsi import RSI
from analysis.indicators.macd import MACD



class TechnicalEngine:


    def __init__(self):

        self.ma = MovingAverage()
        self.rsi = RSI()
        self.macd = MACD()



    def calculate_ma(self, prices, period):

        return self.ma.calculate(
            prices,
            period
        )



    def calculate_rsi(self, prices, period=14):

        return self.rsi.calculate(
            prices,
            period
        )



    def calculate_macd(self, prices):

        return self.macd.calculate(
            prices
        )