from pathlib import Path


def test_main_uses_source_candle_pipeline():
    main_source = Path("main.py").read_text()

    assert "SourceCandlePipeline" in main_source
    assert "source_candle_pipeline" in main_source
    assert "source_candle_pipeline=source_candle_pipeline" in main_source
