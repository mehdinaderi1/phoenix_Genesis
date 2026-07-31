class EvolutionAnalytics:

    def __init__(self, history):
        self.history = history


    def count(self):

        return len(
            self.history.all()
        )


    def best_child(self):

        records = self.history.all()

        if not records:
            return None

        return max(
            records,
            key=lambda r: r.score_after
        )


    def average_improvement(self):

        records = self.history.all()

        if not records:
            return 0


        improvements = [
            r.score_after - r.score_before
            for r in records
        ]


        return sum(improvements) / len(improvements)


    def lineage_growth(self, parent):

        children = self.history.children_of(
            parent
        )

        if not children:
            return 0


        improvements = [
            r.score_after - r.score_before
            for r in children
        ]


        return sum(improvements) / len(improvements)