from execution.paper_position_sizer import PaperPositionSizer


def test_calculate_quantity():

    sizer = PaperPositionSizer()

    quantity = sizer.calculate_quantity(
        balance=1000,
        position_size_percent=1,
        entry_price=65000
    )

    assert quantity == 10 / 65000


def test_zero_balance_returns_zero():

    sizer = PaperPositionSizer()

    quantity = sizer.calculate_quantity(
        balance=0,
        position_size_percent=1,
        entry_price=65000
    )

    assert quantity == 0.0


def test_invalid_position_size_returns_zero():

    sizer = PaperPositionSizer()

    quantity = sizer.calculate_quantity(
        balance=1000,
        position_size_percent=0,
        entry_price=65000
    )

    assert quantity == 0.0


def test_invalid_entry_price_returns_zero():

    sizer = PaperPositionSizer()

    quantity = sizer.calculate_quantity(
        balance=1000,
        position_size_percent=1,
        entry_price=0
    )

    assert quantity == 0.0