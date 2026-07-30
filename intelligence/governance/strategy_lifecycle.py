from intelligence.learning.strategy_version import StrategyVersion


class StrategyLifecycle:


    CREATED = "CREATED"

    CANDIDATE = "CANDIDATE"

    ACTIVE = "ACTIVE"

    CHAMPION = "CHAMPION"

    RETIRED = "RETIRED"

    ARCHIVED = "ARCHIVED"



    def create(
        self,
        strategy: StrategyVersion
    ):

        strategy.status = self.CREATED

        return strategy



    def promote_candidate(
        self,
        strategy: StrategyVersion
    ):

        if strategy.status == self.CREATED:

            strategy.status = self.CANDIDATE


        return strategy



    def activate(
        self,
        strategy: StrategyVersion
    ):

        if strategy.status == self.CANDIDATE:

            strategy.status = self.ACTIVE


        return strategy



    def promote_champion(
        self,
        strategy: StrategyVersion
    ):

        if strategy.status == self.ACTIVE:

            strategy.status = self.CHAMPION


        return strategy



    def retire(
        self,
        strategy: StrategyVersion
    ):

        strategy.status = self.RETIRED

        return strategy



    def archive(
        self,
        strategy: StrategyVersion
    ):

        strategy.status = self.ARCHIVED

        return strategy