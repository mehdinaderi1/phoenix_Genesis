class MarketDataRepository:

    def __init__(self, db):
        self.db = db


    def save_candle(
        self,
        symbol,
        timeframe,
        open_price,
        high,
        low,
        close,
        volume,
        timestamp
    ):

        cursor = self.db.connection.cursor()

        cursor.execute("""
        INSERT INTO market_candles
        (
            symbol,
            timeframe,
            open,
            high,
            low,
            close,
            volume,
            timestamp
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            symbol,
            timeframe,
            open_price,
            high,
            low,
            close,
            volume,
            timestamp
        ))

        self.db.connection.commit()


    def get_latest_candles(self, symbol, limit=10):

        cursor = self.db.connection.cursor()

        cursor.execute("""
        SELECT *
        FROM market_candles
        WHERE symbol=?
        ORDER BY id DESC
        LIMIT ?
        """,
        (symbol, limit))

        return cursor.fetchall()