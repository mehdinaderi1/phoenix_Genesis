from intelligence.lifecycle.lifecycle_state import (
    LifecycleState
)

from intelligence.lifecycle.lifecycle_event import (
    LifecycleEvent
)


class StrategyLifecycleManager:


    def __init__(self, history=None):

        self.history = history
        self.lifecycle_history = history

        @property
        def history(self):

            return self.lifecycle_history



    def _transition(
        self,
        strategy,
        new_state,
        reason
    ):

        old_state = strategy.status

        strategy.status = new_state


        if self.history:

            self.history.add(

                LifecycleEvent(

                    strategy_name=strategy.name,

                    from_state=old_state,

                    to_state=new_state,

                    reason=reason

                )

            )


        return strategy



    def create(self, strategy):

        return self._transition(

            strategy,

            LifecycleState.CREATED.value,

            "strategy created"

        )



    def promote_candidate(self, strategy):

        return self._transition(

            strategy,

            LifecycleState.CANDIDATE.value,

            "strategy promoted to candidate"

        )



    def activate(self, strategy):

        return self._transition(

            strategy,

            LifecycleState.ACTIVE.value,

            "strategy activated"

        )



    def promote_champion(self, strategy):

        return self._transition(

            strategy,

            LifecycleState.CHAMPION.value,

            "strategy promoted to champion"

        )



    def retire(self, strategy):

        return self._transition(

            strategy,

            LifecycleState.RETIRED.value,

            "strategy retired"

        )



    def archive(self, strategy):

        return self._transition(

            strategy,

            LifecycleState.ARCHIVED.value,

            "strategy archived"

        )