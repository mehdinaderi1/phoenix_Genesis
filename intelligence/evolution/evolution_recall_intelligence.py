class EvolutionRecallIntelligence:

    def __init__(
        self,
        recall
    ):
        self.recall = recall


    def analyze(
        self,
        strategy_name
    ):

        history = self.recall.find_lineage(
            strategy_name
        )


        if not history:

            return {
                "known": False,
                "evolution_count": 0,
                "confidence": 0
            }


        successful = 0


        for record in history:

            if record.score_after > record.score_before:
                successful += 1


        confidence = (
            successful / len(history)
        ) * 100


        return {

            "known": True,

            "evolution_count": len(history),

            "successful_evolutions": successful,

            "confidence": confidence

        }