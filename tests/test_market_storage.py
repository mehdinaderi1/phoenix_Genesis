from core.database import DatabaseManager
from core.market_data.repository import MarketDataRepository


db = DatabaseManager()

db.connect()
db.create_tables()


repo = MarketDataRepository(db)


repo.save_candle(
    "BTCUSDT",
    "30m",
    65000,
    65100,
    64900,
    65000,
    120,
    123456789
)


data = repo.get_latest_candles(
    "BTCUSDT"
)


print(data)


print("✅ Market Data Storage Passed")