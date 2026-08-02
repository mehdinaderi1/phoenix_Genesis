class RuntimeTaskQueue:


    def __init__(
        self
    ):

        self.tasks = []



    def add(
        self,
        task
    ):

        self.tasks.append(
            task
        )



    def count(
        self
    ):

        return len(
            self.tasks
        )



    def next_task(
        self
    ):

        if not self.tasks:

            return None


        priority_order = {

            "HIGH": 1,

            "MEDIUM": 2,

            "LOW": 3

        }


        self.tasks.sort(
            key=lambda x:
                priority_order.get(
                    x.priority,
                    99
                )
        )


        return self.tasks.pop(0)