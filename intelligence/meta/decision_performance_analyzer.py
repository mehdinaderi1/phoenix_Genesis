from intelligence.meta.meta_insight import MetaInsight


class DecisionPerformanceAnalyzer:


    def analyze(
        self,
        records
    ):

        if not records:

            return MetaInsight()


        samples = len(records)


        total_quality = sum(
            r.quality_score
            for r in records
        )


        average_quality = (
            total_quality / samples
        )


        confidence_matches = 0


        for record in records:

            if (
                record.validation_status
                == "APPROVED"
                and
                record.confidence >= 60
            ):

                confidence_matches += 1


        confidence_accuracy = (
            confidence_matches / samples
        ) * 100


        if confidence_accuracy >= 80:

            reliability = "HIGH"

        elif confidence_accuracy >= 50:

            reliability = "MEDIUM"

        else:

            reliability = "LOW"


        return MetaInsight(

            samples=samples,

            average_quality=average_quality,

            confidence_accuracy=confidence_accuracy,

            reliability=reliability

        )