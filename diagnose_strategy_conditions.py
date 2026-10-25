import sqlite3
from analysis.timeframe_analyzer import TimeframeAnalyzer
from intelligence.multitimeframe import MultiTimeframeAnalyzer
from intelligence.trading_strategy import BTCMTFTrendAlignmentV1

DB_PATH = "data/phoenix.db"
TIMEFRAMES = ("5m", "15m", "30m", "4H", "1D")
SYMBOL = "BTCUSDT"

connection = sqlite3.connect(
    f"file:{DB_PATH}?mode=ro",
    uri=True,
)

try:
    analyzer = TimeframeAnalyzer()
    analyses = []

    for timeframe in TIMEFRAMES:
        rows = connection.execute(
            """
            SELECT close
            FROM market_candles
            WHERE symbol = ? AND timeframe = ?
            ORDER BY timestamp ASC
            """,
            (SYMBOL, timeframe),
        ).fetchall()

        prices = [float(row[0]) for row in rows]

        if not prices:
            print(f"{timeframe}: NO DATA")
            continue

        result = analyzer.analyze(prices, timeframe)
        analyses.append(result)

        print(
            f"{timeframe}: trend={result.trend} "
            f"signal={result.signal} confidence={result.confidence}"
        )
finally:
    connection.close()

consensus = MultiTimeframeAnalyzer().analyze(analyses)
strategy = BTCMTFTrendAlignmentV1()
states = strategy.states_from_breakdown(consensus.breakdown)
evaluation = strategy.evaluate(states)

print("\n--- STRATEGY DIAGNOSTIC ---")
print("Consensus signal:", consensus.signal)
print("Consensus confidence:", consensus.confidence)
print("Timeframe states:", states)
print("LONG conditions:", strategy.long_conditions)
print("SHORT conditions:", strategy.short_conditions)
print("Evaluation:", evaluation)

print("\n--- CONDITION CHECKS ---")
for timeframe, expected in strategy.long_conditions.items():
    actual = states.get(timeframe)
    print(f"LONG {timeframe}: expected={expected}, actual={actual}, pass={actual == expected}")

for timeframe, expected in strategy.short_conditions.items():
    actual = states.get(timeframe)
    print(f"SHORT {timeframe}: expected={expected}, actual={actual}, pass={actual == expected}")
