from pathlib import Path


def test_main_uses_source_candle_pipeline():
    main_source = Path("main.py").read_text()

    assert "SourceCandlePipeline" in main_source
    assert "source_candle_pipeline" in main_source
    assert "source_candle_pipeline=source_candle_pipeline" in main_source


def test_main_warms_up_historical_mtf_before_cycles():
    main_source = Path("main.py").read_text()

    warmup_marker = "source_candle_pipeline.warm_up("
    cycles_marker = "Starting operational cycles..."

    assert warmup_marker in main_source
    assert cycles_marker in main_source
    assert main_source.index(warmup_marker) < main_source.index(cycles_marker)

    assert 'timeframes=timeframes' in main_source
    assert 'limit=30' in main_source
