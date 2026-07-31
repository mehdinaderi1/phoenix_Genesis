class EvolutionTree:

    def __init__(self, history):
        self.history = history


    def children_of(self, strategy):

        return [
            record.child
            for record in self.history.children_of(strategy)
        ]


    def parent_of(self, strategy):

        for record in self.history.all():

            if record.child == strategy:
                return record.parent

        return None


    def lineage(self, strategy):

        result = []

        current = strategy

        while current:

            result.append(current)

            current = self.parent_of(current)

        return result[::-1]


    def generations(self):

        return [
            record.generation
            for record in self.history.all()
        ]