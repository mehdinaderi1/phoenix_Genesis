import pytest

from experiments.signal_matrix.signal_matrix import StrategySignal
from experiments.signal_matrix.strategy_lane_evaluator import (
    StrategyLane,
    StrategyLaneEvaluator,
)


def test_independent_lanes_keep_opposing_signals():
    evaluator = StrategyLaneEvaluator([
        StrategyLane("ScalpStrategy", "5m"),
        StrategyLane("DailyStrategy", "1D"),
    ])

    matrix = evaluator.collect({
        ("ScalpStrategy", "5m"): StrategySignal(
            "ScalpStrategy", "5m", "BUY", 76
        ),
        ("DailyStrategy", "1D"): StrategySignal(
            "DailyStrategy", "1D", "SELL", 83
        ),
    })

    assert [s.state for s in matrix.all_signals()] == ["BUY", "SELL"]


def test_missing_lane_is_not_evaluated_not_wait():
    evaluator = StrategyLaneEvaluator([
        StrategyLane("ScalpStrategy", "5m"),
        StrategyLane("DailyStrategy", "1D"),
    ])

    matrix = evaluator.collect({
        ("ScalpStrategy", "5m"): StrategySignal(
            "ScalpStrategy", "5m", "NO_SIGNAL"
        ),
    })

    assert [s.state for s in matrix.all_signals()] == [
        "NO_SIGNAL", "NOT_EVALUATED"
    ]


def test_lane_identity_mismatch_is_rejected():
    evaluator = StrategyLaneEvaluator([
        StrategyLane("ScalpStrategy", "5m"),
    ])

    with pytest.raises(ValueError, match="identity mismatch"):
        evaluator.collect({
            ("ScalpStrategy", "5m"): StrategySignal(
                "OtherStrategy", "5m", "BUY", 80
            ),
        })


def test_duplicate_lanes_are_rejected():
    with pytest.raises(ValueError, match="Duplicate"):
        StrategyLaneEvaluator([
            StrategyLane("ScalpStrategy", "5m"),
            StrategyLane("ScalpStrategy", "5m"),
        ])
