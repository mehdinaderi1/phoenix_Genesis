class SignalEngine:

    def analyze(self, indicators, current_price=None):

        signals = []

        ma = indicators.get("ma")
        rsi = indicators.get("rsi")
        macd = indicators.get("macd")

        # Trend Analysis
        if ma is not None and current_price is not None:

            if current_price > ma:
                signals.append("Bullish Trend")

            elif current_price < ma:
                signals.append("Bearish Trend")

            else:
                signals.append("Neutral Trend")

        # RSI Analysis
        if rsi is not None:

            if rsi >= 70:
                signals.append("Overbought")

            elif rsi <= 30:
                signals.append("Oversold")

            else:
                signals.append("Neutral RSI")

        # MACD Analysis
        if macd is not None:

            if macd > 0:
                signals.append("Positive Momentum")

            elif macd < 0:
                signals.append("Negative Momentum")

            else:
                signals.append("Neutral Momentum")

        return signals