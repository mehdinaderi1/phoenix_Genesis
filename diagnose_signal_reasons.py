import sqlite3
from analysis.market_analyzer import MarketAnalyzer

DB_PATH = "data/phoenix.db"
TIMEFRAMES = ("5m", "15m", "30m", "4H", "1D")

connection = sqlite3.connect(
    f"file:{DB_PATH}?mode=ro",
    uri=True,
)

try:
    for timeframe in TIMEFRAMES:
        rows = connection.execute(
            """
            SELECT close
            FROM market_candles
            WHERE symbol = ? AND timeframe = ?
            ORDER BY timestamp ASC
            """,
            ("BTCUSDT", timeframe),
        ).fetchall()

        prices = [float(row[0]) for row in rows]

        print(f"\n--- {timeframe} | candles={len(prices)} ---")

        if not prices:
            print("NO DATA")
            continue

        result = MarketAnalyzer().analyze(prices)

        print("Signals:", result.get("signals"))
        print("Confidence:", result.get("confidence"))
finally:
    connection.close()
