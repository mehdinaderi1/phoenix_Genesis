class RuntimeScheduleDecision:

    def __init__(
        self,
        allowed,
        reason
    ):

        self.allowed = allowed
        self.reason = reason



class RuntimeScheduler:


    def can_process_background(
        self,
        context
    ):

        # Never run background intelligence
        # during critical market conditions

        if context.critical_market:

            return RuntimeScheduleDecision(
                False,
                "critical_market"
            )


        # Protect active positions

        if context.open_position:

            return RuntimeScheduleDecision(
                False,
                "position_active"
            )


        return RuntimeScheduleDecision(
            True,
            "runtime_available"
        )