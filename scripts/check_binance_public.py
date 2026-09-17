import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from exchanges.binance_exchange import BinanceExchange


def main():
    exchange = BinanceExchange(timeout=10)

    print("=" * 55)
    print("Phoenix Genesis - Binance Public Connectivity Check")
    print("=" * 55)

    print("[1] Connecting to Binance...")
    result = exchange.connect()
    print(f"    {result}")

    print("[2] Reading BTCUSDT price...")
    price = exchange.get_price("BTCUSDT")
    print(f"    BTCUSDT = {price}")

    print("[3] Reading BTCUSDT 1m candle...")
    candle = exchange.get_candle("BTCUSDT", "1m")
    print(f"    Candle = {candle}")

    print("[4] Reading BTCUSDT historical 1m candles...")
    candles = exchange.get_historical_candles(
        "BTCUSDT",
        "1m",
        5
    )
    print(f"    Candles received = {len(candles)}")

    if len(candles) != 5:
        raise AssertionError(
            f"Expected 5 candles, received {len(candles)}"
        )

    print("=" * 55)
    print("BINANCE PUBLIC CONNECTIVITY: PASS")
    print("Real orders: DISABLED")
    print("=" * 55)


if __name__ == "__main__":
    main()
