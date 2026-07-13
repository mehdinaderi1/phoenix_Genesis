class MovingAverage:


    @staticmethod
    def calculate(values, period):

        if len(values) < period:
            return None


        recent_values = values[-period:]


        return sum(recent_values) / period