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

        average_confidence = sum(confidences) / len(confidences)

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