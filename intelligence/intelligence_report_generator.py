from intelligence.intelligence_report import IntelligenceReport


class IntelligenceReportGenerator:


    def generate(self, records):

        if not records:

            return IntelligenceReport(

                total_decisions=0,

                approval_rate=0,

                average_confidence=0,

                average_quality=0,

                best_action=None,

                best_regime=None
            )


        total = len(records)


        approved = len(
            [
                r for r in records
                if r.validation_status == "APPROVED"
            ]
        )


        approval_rate = (
            approved / total
        ) * 100


        average_confidence = sum(
            r.confidence for r in records
        ) / total


        average_quality = sum(
            r.quality_score for r in records
        ) / total



        actions = {}

        regimes = {}


        for record in records:

            actions[record.action] = (
                actions.get(record.action, 0) + 1
            )


            regimes[record.regime] = (
                regimes.get(record.regime, 0) + 1
            )



        best_action = max(
            actions,
            key=actions.get
        )


        best_regime = max(
            regimes,
            key=regimes.get
        )


        return IntelligenceReport(

            total_decisions=total,

            approval_rate=approval_rate,

            average_confidence=average_confidence,

            average_quality=average_quality,

            best_action=best_action,

            best_regime=best_regime
        )