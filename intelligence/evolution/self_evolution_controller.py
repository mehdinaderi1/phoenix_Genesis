class StrategyLineage:


    def __init__(
        self,
        tree
    ):

        self.tree = tree



    def root_of(
        self,
        strategy
    ):

        lineage = self.tree.lineage(
            strategy
        )

        if not lineage:

            return None


        return lineage[0]



    def depth_of(
        self,
        strategy
    ):

        lineage = self.tree.lineage(
            strategy
        )

        if not lineage:

            return 0


        return len(lineage) - 1



    def family(
        self,
        strategy
    ):

        root = self.root_of(
            strategy
        )

        if not root:

            return []


        return self._collect_family(
            root
        )



    def _collect_family(
        self,
        strategy,
        visited=None
    ):

        if visited is None:

            visited = set()



        if strategy in visited:

            return []



        visited.add(
            strategy
        )



        result = [

            strategy

        ]



        children = self.tree.children_of(
            strategy
        )



        for child in children:


            result.extend(

                self._collect_family(

                    child,

                    visited

                )

            )



        return result