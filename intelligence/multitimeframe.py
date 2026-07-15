from intelligence.consensus import ConsensusResult


class MultiTimeframeAnalyzer:

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

        confidences = [
            item.confidence
            for item in analyses
        ]

        if len(set(signals)) == 1:
            final_signal = signals[0]
        else:
            final_signal = "WAIT"

        average_confidence = sum(confidences) / len(confidences)

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
            confidence=average_confidence
        )