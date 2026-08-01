class LifecycleHistory:


    def __init__(self):

        self.events = []


    def add(self, event):

        self.events.append(event)



    def get_all(self):

        return self.events



    def latest(self):

        if not self.events:

            return None

        return self.events[-1]