from types import SimpleNamespace

import pytest

from notifications.signal_outbox import SignalOutbox
from notifications.signal_publisher import SignalPublisher


@pytest.fixture
def publisher(tmp_path):
    outbox = SignalOutbox(tmp_path / "notifications.db")
    return SignalPublisher(outbox), outbox


def make_proposal(action="BUY", status="APPROVED"):
    return SimpleNamespace(
        action=action,
        status=status,
        reason="Test signal",
        confidence=0.91,
        risk_status="ACCEPTABLE",
    )


def make_observation(
    symbol="BTCUSDT",
    price=65000.0,
    timestamp="2026-10-09T12:00:00+00:00",
):
    return SimpleNamespace(
        symbol=symbol,
        price=price,
        timestamp=timestamp,
    )


def make_boundaries():
    return {
        "5m": {
            "candle_start": 1_760_000_000,
            "next_boundary": 1_760_000_300,
            "duration_seconds": 300,
            "age_seconds": 10,
            "is_closed": False,
        }
    }


def test_approved_buy_signal_is_recorded(publisher):
    service, outbox = publisher

    signal = service.publish(
        make_proposal(),
        make_observation(),
        make_boundaries(),
    )

    assert signal is not None
    assert signal["action"] == "BUY"
    assert signal["status"] == "APPROVED"
    assert signal["symbol"] == "BTCUSDT"
    assert signal["reference_price"] == 65000.0
    assert signal["timeframe"] == "5m"
    assert outbox.get_signal(signal["signal_id"]) == signal
    assert outbox.get_message(signal["signal_id"])["status"] == "PENDING"


@pytest.mark.parametrize(
    "proposal",
    [
        None,
        make_proposal(action="WAIT"),
        make_proposal(status="REJECTED"),
    ],
)
def test_non_approved_or_non_directional_proposals_are_ignored(
    publisher, proposal
):
    service, outbox = publisher

    result = service.publish(
        proposal,
        make_observation(),
        make_boundaries(),
    )

    assert result is None
    assert outbox.get_pending_messages() == []


@pytest.mark.parametrize(
    "observation",
    [
        None,
        make_observation(symbol="", price=65000.0),
        make_observation(price=0),
        make_observation(price="not-a-price"),
    ],
)
def test_invalid_observation_is_ignored(publisher, observation):
    service, outbox = publisher

    result = service.publish(
        make_proposal(),
        observation,
        make_boundaries(),
    )

    assert result is None
    assert outbox.get_pending_messages() == []


def test_missing_candle_boundary_is_not_published(publisher):
    service, outbox = publisher

    result = service.publish(
        make_proposal(),
        make_observation(),
        {"5m": None},
    )

    assert result is None
    assert outbox.get_pending_messages() == []


def test_repeated_same_signal_is_idempotent(publisher):
    service, outbox = publisher
    arguments = (
        make_proposal(),
        make_observation(),
        make_boundaries(),
    )

    first = service.publish(*arguments)
    second = service.publish(*arguments)

    assert first == second
    assert len(outbox.get_pending_messages()) == 1


def test_repeated_same_signal_with_later_generated_at_preserves_original_record(publisher):
    service, outbox = publisher
    boundaries = make_boundaries()

    first = service.publish(
        make_proposal(),
        make_observation(price=65000.0, timestamp="2026-10-09T12:00:00+00:00"),
        boundaries,
        generated_at="2026-10-09T12:01:00+00:00",
    )
    second = service.publish(
        make_proposal(),
        make_observation(price=65010.0, timestamp="2026-10-09T12:02:00+00:00"),
        boundaries,
        generated_at="2026-10-09T12:02:00+00:00",
    )

    assert second == first
    assert outbox.get_signal(first["signal_id"]) == first
    assert len(outbox.get_pending_messages()) == 1

def test_changed_payload_for_same_signal_id_is_not_silently_accepted(publisher):
    service, _ = publisher
    boundaries = make_boundaries()

    service.publish(
        make_proposal(),
        make_observation(),
        boundaries,
    )

    with pytest.raises(Exception):
        service.publish(
            make_proposal()._replace(reason="Changed reason")
            if hasattr(make_proposal(), "_replace")
            else SimpleNamespace(
                action="BUY",
                status="APPROVED",
                reason="Changed reason",
                confidence=0.91,
                risk_status="ACCEPTABLE",
            ),
            make_observation(),
            boundaries,
        )

def test_primary_timeframe_is_selected_when_multiple_timeframes_exist(publisher):
    service, outbox = publisher
    boundaries = {
        "15m": {
            "candle_start": 1_760_000_900,
            "next_boundary": 1_760_001_800,
            "duration_seconds": 900,
            "age_seconds": 10,
            "is_closed": False,
        },
        "5m": make_boundaries()["5m"],
    }

    signal = service.publish(
        make_proposal(),
        make_observation(),
        boundaries,
    )

    assert signal is not None
    assert signal["timeframe"] == "5m"
    assert signal["generated_at"] == "2026-10-09T12:00:00Z"
    assert signal["candle_start"] == "2025-10-09T08:53:20Z"
    assert outbox.get_signal(signal["signal_id"]) == signal


def test_missing_primary_timeframe_is_not_published(publisher):
    service, outbox = publisher
    boundaries = {
        "15m": {
            "candle_start": 1_760_000_900,
            "next_boundary": 1_760_001_800,
            "duration_seconds": 900,
            "age_seconds": 10,
            "is_closed": False,
        }
    }

    result = service.publish(
        make_proposal(),
        make_observation(),
        boundaries,
    )

    assert result is None
    assert outbox.get_pending_messages() == []


