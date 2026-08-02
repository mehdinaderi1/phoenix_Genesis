class RuntimeContext:

    def __init__(
        self,
        signal_ready=False,
        open_position=False,
        critical_market=False,
        memory_queries=0,
        analysis_depth=0,
        evolution_requested=False,
        strategy=None
    ):

        self.signal_ready = signal_ready

        self.open_position = open_position

        self.critical_market = critical_market

        self.memory_queries = memory_queries

        self.analysis_depth = analysis_depth

        self.evolution_requested = (
            evolution_requested
        )

        self.strategy = strategy



    def to_dict(
        self
    ):

        return {

            "signal_ready":
                self.signal_ready,

            "open_position":
                self.open_position,

            "critical_market":
                self.critical_market,

            "memory_queries":
                self.memory_queries,

            "analysis_depth":
                self.analysis_depth,

            "evolution_requested":
                self.evolution_requested,

            "strategy":
                self.strategy
        }