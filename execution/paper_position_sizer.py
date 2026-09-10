class PaperPositionSizer:

    def calculate_quantity(
        self,
        balance,
        position_size_percent,
        entry_price
    ):
        if balance is None or balance <= 0:
            return 0.0

        if (
            position_size_percent is None
            or position_size_percent <= 0
        ):
            return 0.0

        if entry_price is None or entry_price <= 0:
            return 0.0

        capital = balance * (
            position_size_percent / 100
        )

        quantity = capital / entry_price

        return quantity