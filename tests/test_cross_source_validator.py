from core.market_data.cross_source_validator import CrossSourceValidator


def test_matching_sources_are_valid():
    validator = CrossSourceValidator(max_difference_percent=1.0)

    result = validator.validate(
        {"binance": 65000.0, "coinmarketcap": 65020.0}
    )

    assert result.status == "VALID"
    assert result.primary_source == "binance"
    assert result.reference_source == "coinmarketcap"
    assert result.price == 65000.0
    assert result.difference_percent < 1.0


def test_large_source_difference_is_suspect():
    validator = CrossSourceValidator(max_difference_percent=1.0)

    result = validator.validate(
        {"binance": 65000.0, "coinmarketcap": 68000.0}
    )

    assert result.status == "SUSPECT"
    assert result.primary_source == "binance"
    assert result.reference_source == "coinmarketcap"
    assert result.price == 65000.0
    assert result.difference_percent > 1.0


def test_single_source_is_insufficient():
    validator = CrossSourceValidator(max_difference_percent=1.0)

    result = validator.validate(
        {"binance": 65000.0}
    )

    assert result.status == "INSUFFICIENT"
    assert result.primary_source == "binance"
    assert result.reference_source is None
    assert result.price == 65000.0
    assert result.difference_percent is None


def test_no_sources_are_blind():
    validator = CrossSourceValidator(max_difference_percent=1.0)

    result = validator.validate({})

    assert result.status == "BLIND"
    assert result.primary_source is None
    assert result.reference_source is None
    assert result.price is None
    assert result.difference_percent is None
