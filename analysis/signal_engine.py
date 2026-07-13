class SignalEngine:

    def analyze(self, indicators):

        signals = []

        ma = indicators.get("ma")
        rsi = indicators.get("rsi")
        macd = indicators.get("macd")

        # Trend Analysis
        if ma > 0:
            signals.append("Bullish Trend")

        # RSI Analysis
        if rsi >= 70:
            signals.append("Overbought")
        elif rsi <= 30:
            signals.append("Oversold")
        else:
            signals.append("Neutral RSI")

        # MACD Analysis
        if macd > 0:
            signals.append("Positive Momentum")
        else:
            signals.append("Negative Momentum")

        return signals