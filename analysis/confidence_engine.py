class ConfidenceEngine:

    def calculate(self, signals):

        score = 50

        for signal in signals:

            if signal == "Bullish Trend":
                score += 15

            elif signal == "Positive Momentum":
                score += 15

            elif signal == "Overbought":
                score -= 10

            elif signal == "Bearish Trend":
                score -= 15

            elif signal == "Negative Momentum":
                score -= 15

        if score > 100:
            score = 100

        if score < 0:
            score = 0

        return score