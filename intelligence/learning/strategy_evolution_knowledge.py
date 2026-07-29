from dataclasses import dataclass


@dataclass(slots=True)
class StrategyKnowledge:

    strategy: str

    generations: int

    average_score: float

    average_success_rate: float

    improvements: int

    retirements: int



class StrategyEvolutionKnowledge:


    def __init__(
        self,
        history
    ):

        self.history = history



    def analyze(
        self,
        strategy_name
    ):

        records = self.history.by_strategy(
            strategy_name
        )


        if not records:

            return None



        generations = len(records)


        average_score = (

            sum(
                r.score
                for r in records
            )

            / generations

        )


        average_success_rate = (

            sum(
                r.success_rate
                for r in records
            )

            / generations

        )


        improvements = sum(

            1

            for r in records

            if r.decision == "IMPROVE"

        )


        retirements = sum(

            1

            for r in records

            if r.decision == "RETIRE"

        )


        return StrategyKnowledge(

            strategy=strategy_name,

            generations=generations,

            average_score=round(
                average_score,
                2
            ),

            average_success_rate=round(
                average_success_rate,
                2
            ),

            improvements=improvements,

            retirements=retirements

        )