class RuntimeTask:

    def __init__(
        self,
        name,
        priority,
        payload=None
    ):

        self.name = name

        self.priority = priority

        self.payload = payload

        self.status = "PENDING"