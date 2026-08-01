class EvolutionLineage:

    def __init__(self):
        self.nodes = []


    def add(
        self,
        record
    ):
        self.nodes.append(
            record
        )


    def all(self):

        return self.nodes


    def find_lineage(
        self,
        strategy
    ):

        result = []

        current = strategy


        while current:

            found = None

            for record in self.nodes:

                if record.child == current:

                    found = record
                    break


            if not found:
                break


            result.insert(
                0,
                found
            )

            current = found.parent


        return result


    def children(
        self,
        strategy
    ):

        return [

            record

            for record in self.nodes

            if record.parent == strategy

        ]


    def latest(
        self,
        strategy
    ):

        lineage = self.find_lineage(
            strategy
        )

        if not lineage:
            return None


        return lineage[-1]