from analysis.technical_engine import TechnicalEngine



class MarketAnalyzer:


    def __init__(self):

        self.technical = TechnicalEngine()



    def analyze(self, prices):


        ma = self.technical.calculate_ma(
            prices,
            5
        )


        rsi = self.technical.calculate_rsi(
            prices,
            14
        )


        macd = self.technical.calculate_macd(
            prices
        )


        result = {

            "ma": ma,

            "rsi": rsi,

            "macd": macd

        }


        return result