from intelligence.historical_insight import HistoricalInsight


class LearningAnalyzer:


    def analyze(self, records):

        if not records:

            return HistoricalInsight(

                pattern="UNKNOWN",

                samples=0,

                average_confidence=0,

                average_quality=0,

                reliability="UNKNOWN"

            )


        samples = len(records)


        average_confidence = sum(
            r.confidence for r in records
        ) / samples


        average_quality = sum(
            r.quality_score for r in records
        ) / samples


        if average_quality >= 80:

            reliability = "HIGH"

        elif average_quality >= 50:

            reliability = "MEDIUM"

        else:

            reliability = "LOW"


        return HistoricalInsight(

            pattern=f"{records[0].regime} + {records[0].action}",

            samples=samples,

            average_confidence=average_confidence,

            average_quality=average_quality,

            reliability=reliability

        )