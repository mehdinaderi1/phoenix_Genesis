class EvolutionExecution:

    def __init__(
        self,
        controller
    ):
        self.controller = controller


    def execute(
        self,
        strategy,
        score
    ):

        result = self.controller.run(
            strategy,
            score
        )


        return {

            "executed": True,

            "strategy": strategy,

            "result": result

        }