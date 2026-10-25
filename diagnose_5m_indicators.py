import sqlite3

from analysis.indicators.moving_average import MovingAverage
from analysis.indicators.macd import MACD

DB_PATH = "data/phoenix.db"
SYMBOL = "BTCUSDT"
TIMEFRAME = "5m"

connection = sqlite3.connect(
    f"file:{DB_PATH}?mode=ro",
    uri=True,
)

try:
    rows = connection.execute(
        """
        SELECT timestamp, close
        FROM market_candles
        WHERE symbol = ? AND timeframe = ?
        ORDER BY timestamp ASC
        """,
        (SYMBOL, TIMEFRAME),
    ).fetchall()
finally:
    connection.close()

prices = [float(row[1]) for row in rows]

print(f"Candles: {len(rows)}")
print(f"Latest timestamp: {rows[-1][0] if rows else 'NO DATA'}")

if not prices:
    print("No price data")
elif len(prices) < 26:
    print("Not enough data for MACD")
else:
    last_close = prices[-1]
    ma5 = MovingAverage.calculate(prices, 5)
    macd_value = MACD.calculate(prices)

    print("\n--- INDICATOR VALUES ---")
    print(f"Last close: {last_close:.8f}")
    print(f"MA(5):      {ma5:.8f}")
    print(f"MACD(12,26): {macd_value:.8f}")
    print(f"Price > MA: {last_close > ma5}")
    print(f"MACD > 0:   {macd_value > 0}")

    print("\n--- LAST 10 CLOSES ---")
    for timestamp, close in rows[-10:]:
        print(f"{timestamp}: {close:.8f}")
