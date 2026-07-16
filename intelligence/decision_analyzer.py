class DecisionAnalyzer:

    def analyze(self, records):

        total = len(records)

        approved = len(
            [
                r for r in records
                if r.validation_status == "APPROVED"
            ]
        )

        rejected = total - approved

        if total == 0:
            average_confidence = 0
        else:
            average_confidence = sum(
                r.confidence for r in records
            ) / total


        return {
            "total_decisions": total,
            "approved": approved,
            "rejected": rejected,
            "average_confidence": average_confidence
        }