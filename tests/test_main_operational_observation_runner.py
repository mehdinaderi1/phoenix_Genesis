from pathlib import Path


def test_main_uses_operational_observation_runner():
    main_source = Path("main.py").read_text()

    assert "OperationalObservationRunner" in main_source
    assert "observation_runner" in main_source
    assert "observation_runner.run(" in main_source
