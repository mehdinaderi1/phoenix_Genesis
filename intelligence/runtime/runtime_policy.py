class RuntimePolicy:


    def can_evolve(
        self,
        context
    ):

        if context.critical_market:

            return False


        if context.open_position:

            return False


        return True



    def prioritize_action(
        self,
        context
    ):

        if context.signal_ready:

            return "ACTION"


        if context.evolution_requested:

            return "LEARNING"


        return "WAIT"