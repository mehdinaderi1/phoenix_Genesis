from core.database import DatabaseManager
from core.market_data.pipeline import MarketDataPipeline
from exchanges.mock_exchange import MockExchange


db = DatabaseManager()

db.connect()
db.create_tables()


exchange = MockExchange()


pipeline = MarketDataPipeline(
    exchange,
    db
)


candle = pipeline.fetch_and_store(
    "BTCUSDT",
    "1m"
)


print(candle)


assert "timestamp" in candle
assert "open" in candle
assert "high" in candle
assert "low" in candle
assert "close" in candle
assert "volume" in candle

print("✅ Market Data Pipeline Passed")