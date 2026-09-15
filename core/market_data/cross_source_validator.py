from dataclasses import dataclass


@dataclass(frozen=True)
class CrossSourceValidationResult:
    status: str
    primary_source: str | None
    reference_source: str | None
    price: float | None
    difference_percent: float | None


class CrossSourceValidator:
    def __init__(self, max_difference_percent=1.0):
        if max_difference_percent < 0:
            raise ValueError("max_difference_percent must not be negative")
        self.max_difference_percent = float(max_difference_percent)

    def validate(self, prices):
        if not prices:
            return CrossSourceValidationResult(
                status="BLIND",
                primary_source=None,
                reference_source=None,
                price=None,
                difference_percent=None,
            )

        valid_prices = {
            source: float(price)
            for source, price in prices.items()
            if price is not None
        }

        if not valid_prices:
            return CrossSourceValidationResult(
                status="BLIND",
                primary_source=None,
                reference_source=None,
                price=None,
                difference_percent=None,
            )

        primary_source = next(iter(valid_prices))
        primary_price = valid_prices[primary_source]

        if len(valid_prices) == 1:
            return CrossSourceValidationResult(
                status="INSUFFICIENT",
                primary_source=primary_source,
                reference_source=None,
                price=primary_price,
                difference_percent=None,
            )

        reference_source = next(
            source
            for source in valid_prices
            if source != primary_source
        )
        reference_price = valid_prices[reference_source]

        difference_percent = (
            abs(primary_price - reference_price)
            / primary_price
            * 100.0
        ) if primary_price != 0 else (
            0.0 if reference_price == 0 else float("inf")
        )

        status = (
            "VALID"
            if difference_percent <= self.max_difference_percent
            else "SUSPECT"
        )

        return CrossSourceValidationResult(
            status=status,
            primary_source=primary_source,
            reference_source=reference_source,
            price=primary_price,
            difference_percent=difference_percent,
        )
