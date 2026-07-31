class RollbackEngine:

    def __init__(self, history):
        self.history = history


    def previous_version(self, strategy):

        for record in self.history.all():

            if record.child == strategy:
                return record.parent

        return None


    def can_rollback(self, strategy):

        return (
            self.previous_version(strategy)
            is not None
        )


    def rollback(self, strategy):

        parent = self.previous_version(
            strategy
        )

        if not parent:
            return {
                "rolled_back": False,
                "strategy": strategy,
                "previous": None
            }


        return {
            "rolled_back": True,
            "strategy": parent,
            "previous": strategy
        }