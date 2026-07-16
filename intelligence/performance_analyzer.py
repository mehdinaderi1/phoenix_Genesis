class PerformanceAnalyzer:


    def analyze(self, records):

        if not records:

            return {
                "total_decisions": 0,
                "approved": 0,
                "rejected": 0,
                "approval_rate": 0,
                "average_confidence": 0,
                "by_regime": {},
                "by_action": {}
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



        by_regime = {}


        for record in records:

            regime = record.regime


            if regime not in by_regime:

                by_regime[regime] = {
                    "total": 0,
                    "approved": 0
                }


            by_regime[regime]["total"] += 1


            if record.validation_status == "APPROVED":

                by_regime[regime]["approved"] += 1



        for regime, data in by_regime.items():

            data["rate"] = (
                data["approved"]
                /
                data["total"]
            ) * 100



        by_action = {}


        for record in records:

            action = record.action


            if action not in by_action:

                by_action[action] = {
                    "total": 0,
                    "approved": 0
                }


            by_action[action]["total"] += 1


            if record.validation_status == "APPROVED":

                by_action[action]["approved"] += 1



        return {

            "total_decisions": total,

            "approved": approved,

            "rejected": rejected,

            "approval_rate": approval_rate,

            "average_confidence": average_confidence,

            "by_regime": by_regime,

            "by_action": by_action

        }