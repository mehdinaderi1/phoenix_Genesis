from intelligence.learning.meta_learning_flow import (
    MetaLearningFlow
)


class StrategyIntelligenceService:


    def __init__(self):

        self.flow = MetaLearningFlow()



    def analyze(
        self,
        strategy_context,
        knowledge
    ):

        return self.flow.run(

            strategy_context,

            knowledge

        )