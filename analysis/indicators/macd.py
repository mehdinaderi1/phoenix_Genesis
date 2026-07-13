class MACD:


    @staticmethod
    def ema(values, period):

        if len(values) < period:
            return None


        multiplier = 2 / (period + 1)

        ema_value = sum(values[:period]) / period


        for price in values[period:]:

            ema_value = (
                (price - ema_value) * multiplier
                + ema_value
            )


        return ema_value



    @staticmethod
    def calculate(
        prices,
        fast_period=12,
        slow_period=26
    ):

        fast_ema = MACD.ema(
            prices,
            fast_period
        )


        slow_ema = MACD.ema(
            prices,
            slow_period
        )


        if fast_ema is None or slow_ema is None:
            return None


        return fast_ema - slow_ema