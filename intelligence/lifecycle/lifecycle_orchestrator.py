from intelligence.lifecycle.lifecycle_service import (
    LifecycleService
)


class LifecycleOrchestrator:


    def __init__(self):

        self.lifecycle_service = LifecycleService()



    def run(self, history):

        return self.lifecycle_service.evaluate(
            history
        )