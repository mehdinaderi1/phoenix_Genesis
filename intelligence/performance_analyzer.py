class PerformanceAnalyzer:


    def analyze(self, records):

        if not records:
            return {
                "total_decisions": 0,
                "approved": 0,
                "rejected": 0,
                "approval_rate": 0,
                "average_confidence": 0
            }


        total = len(records)

        approved = len(
            [
                r for r in records
                if r.validation_status == "APPROVED"
            ]
        )


        rejected = total - approved


        average_confidence = sum(
            r.confidence for r in records
        ) / total


        approval_rate = (
            approved / total
        ) * 100


        return {

            "total_decisions": total,

            "approved": approved,

            "rejected": rejected,

            "approval_rate": approval_rate,

            "average_confidence": average_confidence

        }