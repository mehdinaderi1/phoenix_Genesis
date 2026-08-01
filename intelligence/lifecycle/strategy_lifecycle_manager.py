from intelligence.lifecycle.lifecycle_state import (
    LifecycleState
)


class StrategyLifecycleManager:


    def create(self, strategy):

        strategy.status = LifecycleState.CREATED.value

        return strategy



    def promote_candidate(self, strategy):

        strategy.status = LifecycleState.CANDIDATE.value

        return strategy



    def activate(self, strategy):

        strategy.status = LifecycleState.ACTIVE.value

        return strategy



    def promote_champion(self, strategy):

        strategy.status = LifecycleState.CHAMPION.value

        return strategy



    def retire(self, strategy):

        strategy.status = LifecycleState.RETIRED.value

        return strategy



    def archive(self, strategy):

        strategy.status = LifecycleState.ARCHIVED.value

        return strategy