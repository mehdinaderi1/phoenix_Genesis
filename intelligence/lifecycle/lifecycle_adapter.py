from intelligence.lifecycle.lifecycle_event import (
    LifecycleEvent
)

from intelligence.lifecycle.lifecycle_state import (
    LifecycleState
)


class LifecycleAdapter:


    def __init__(
        self,
        lifecycle_manager
    ):

        self.lifecycle_manager = lifecycle_manager



    def register_evolved_strategy(
        self,
        strategy
    ):

        self.lifecycle_manager.create(
            strategy
        )


        self.lifecycle_manager.promote_candidate(
            strategy
        )


        return strategy



    def activate_evolved_strategy(
        self,
        strategy
    ):

        self.lifecycle_manager.activate(
            strategy
        )


        return strategy