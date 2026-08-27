from intelligence.meta.meta_confidence_adapter import (
    MetaConfidenceAdapter
)


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