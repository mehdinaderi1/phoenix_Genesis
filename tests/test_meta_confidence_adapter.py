from intelligence.meta.meta_confidence_adapter import (
    MetaConfidenceAdapter
)

from types import SimpleNamespace


def test_meta_learning_reduces_confidence():

    adapter = MetaConfidenceAdapter()


    result = adapter.adjust(
        80,
        {
            "confidence_adjustment": -10
        }
    )


    assert result == 70



def test_meta_learning_increases_confidence():

    adapter = MetaConfidenceAdapter()


    result = adapter.adjust(
        80,
        {
            "confidence_adjustment": 10
        }
    )


    assert result == 90



def test_meta_learning_keeps_confidence_bounds():

    adapter = MetaConfidenceAdapter()


    result = adapter.adjust(
        95,
        {
            "confidence_adjustment": 20
        }
    )


    assert result == 100


def test_meta_confidence_keeps_confidence_when_learning_is_none():

    adapter = MetaConfidenceAdapter()

    result = adapter.adjust(
        80,
        None
    )

    assert result == 80


def test_meta_confidence_keeps_lower_bound():

    adapter = MetaConfidenceAdapter()

    result = adapter.adjust(
        5,
        {
            "confidence_adjustment": -20
        }
    )

    assert result == 0


def test_meta_confidence_accepts_object_learning_result():

    adapter = MetaConfidenceAdapter()

    learning = SimpleNamespace(
        confidence_adjustment=10
    )

    result = adapter.adjust(
        80,
        learning
    )

    assert result == 90