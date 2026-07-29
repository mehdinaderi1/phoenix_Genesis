from intelligence.learning.meta_learning_engine import (
    MetaLearningEngine
)

from intelligence.enhanced_strategy_context import (
    EnhancedStrategyContextBuilder
)


class MetaLearningFlow:


    def __init__(self):

        self.engine = MetaLearningEngine()

        self.builder = EnhancedStrategyContextBuilder()



    def run(
        self,
        strategy_context,
        knowledge
    ):

        insight = self.engine.analyze(

            knowledge

        )


        context = self.builder.build(

            strategy_context,

            insight

        )


        return context