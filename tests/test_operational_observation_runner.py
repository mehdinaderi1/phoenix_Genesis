from core.market_data.operational_observation_runner import OperationalObservationRunner


class FakeOperationalRuntime:
    def __init__(self):
        self.calls = []

    def run(
        self,
        symbol="BTCUSDT",
        cycles=1,
        continue_on_error=False
    ):
        self.calls.append((
            symbol,
            cycles,
            continue_on_error
        ))
        return [
            {"cycle_number": index}
            for index in range(1, cycles + 1)
        ]


def test_runner_repeats_operational_runtime():
    runtime = FakeOperationalRuntime()
    sleeps = []

    def fake_sleep(seconds):
        sleeps.append(seconds)

    runner = OperationalObservationRunner(
        runtime=runtime,
        sleep_fn=fake_sleep
    )

    results = runner.run(
        symbol="BTCUSDT",
        cycles=3,
        interval_seconds=10,
        continue_on_error=True
    )

    assert len(results) == 3
    assert [result["cycle_number"] for result in results] == [1, 2, 3]
    assert runtime.calls == [
        ("BTCUSDT", 1, True),
        ("BTCUSDT", 1, True),
        ("BTCUSDT", 1, True),
    ]
    assert sleeps == [10, 10]


def test_runner_rejects_invalid_cycles():
    runtime = FakeOperationalRuntime()
    runner = OperationalObservationRunner(
        runtime=runtime
    )

    try:
        runner.run(cycles=0)
    except ValueError as exc:
        assert str(exc) == "cycles must be greater than zero"
    else:
        raise AssertionError("ValueError was expected")


def test_runner_rejects_negative_interval():
    runtime = FakeOperationalRuntime()
    runner = OperationalObservationRunner(
        runtime=runtime
    )

    try:
        runner.run(cycles=2, interval_seconds=-1)
    except ValueError as exc:
        assert str(exc) == "interval_seconds must be greater than or equal to zero"
    else:
        raise AssertionError("ValueError was expected")
