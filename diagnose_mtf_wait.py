import sqlite3

from analysis.timeframe_analyzer import TimeframeAnalyzer
from intelligence.multitimeframe import MultiTimeframeAnalyzer

DB_PATH = "data/phoenix.db"
SYMBOL = "BTCUSDT"
TIMEFRAMES = ("5m", "15m", "30m", "4H", "1D")

connection = sqlite3.connect(
    f"file:{DB_PATH}?mode=ro",
    uri=True,
)

analyzer = TimeframeAnalyzer()
mtf_analyzer = MultiTimeframeAnalyzer()
analyses = []

try:
    for timeframe in TIMEFRAMES:
        rows = connection.execute(
            """
            SELECT timestamp, close
            FROM market_candles
            WHERE symbol = ? AND timeframe = ?
            ORDER BY timestamp ASC
            """,
            (SYMBOL, timeframe),
        ).fetchall()

        prices = [float(row[1]) for row in rows]

        if not prices:
            print(f"{timeframe}: NO DATA")
            continue

        result = analyzer.analyze(prices, timeframe)
        analyses.append(result)

        print(
            f"{timeframe}: candles={len(prices)} "
            f"last_ts={rows[-1][0]} "
            f"last_close={prices[-1]:.8f} "
            f"trend={result.trend} "
            f"signal={result.signal} "
            f"confidence={result.confidence}"
        )

    print("\n--- MTF RESULT ---")

    consensus = mtf_analyzer.analyze(analyses)

    print(f"Trend={consensus.trend}")
    print(f"Signal={consensus.signal}")
    print(f"Confidence={consensus.confidence}")
    print(f"Breakdown={consensus.breakdown}")

finally:
    connection.close()
