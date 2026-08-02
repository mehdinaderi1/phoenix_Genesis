class IntelligenceBudget:

    def __init__(
        self,
        max_memory_lookup=5,
        max_evolution_checks=1,
        max_analysis_depth=3,
        max_decision_time_ms=1000
    ):

        self.max_memory_lookup = (
            max_memory_lookup
        )

        self.max_evolution_checks = (
            max_evolution_checks
        )

        self.max_analysis_depth = (
            max_analysis_depth
        )

        self.max_decision_time_ms = (
            max_decision_time_ms
        )


    def allow_memory_lookup(
        self,
        count
    ):

        return (
            count <= self.max_memory_lookup
        )


    def allow_evolution_check(
        self,
        count
    ):

        return (
            count <= self.max_evolution_checks
        )


    def allow_analysis_depth(
        self,
        depth
    ):

        return (
            depth <= self.max_analysis_depth
        )