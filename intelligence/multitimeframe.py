from intelligence.consensus import ConsensusResult


class MultiTimeframeAnalyzer:

    def get_weight(self, timeframe):

        weights = {
            "30m": 1,
            "4H": 2,
            "Daily": 3
        }

        return weights.get(timeframe, 1)

    def analyze(self, analyses):

        if not analyses:
            return ConsensusResult(
                trend="UNKNOWN",
                signal="WAIT",
                confidence=0
            )

        signals = [
            item.signal
            for item in analyses
        ]

        weighted_sum = 0
        total_weight = 0

        for item in analyses:
            weight = self.get_weight(item.timeframe)

            weighted_sum += item.confidence * weight
            total_weight += weight

        average_confidence = weighted_sum / total_weight

        if len(set(signals)) == 1:
            final_signal = signals[0]
            final_confidence = average_confidence

        else:
            final_signal = "WAIT"
            final_confidence = average_confidence * 0.5

        trends = [
            item.trend
            for item in analyses
        ]

        final_trend = max(
            set(trends),
            key=trends.count
        )

        return ConsensusResult(
            trend=final_trend,
            signal=final_signal,
            confidence=final_confidence
        )