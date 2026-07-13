class MarketDataRepository:

    def __init__(self, db):
        self.db = db


    def candle_exists(self, symbol, timeframe, timestamp):

        cursor = self.db.connection.cursor()

        cursor.execute("""
        SELECT COUNT(*)
        FROM market_candles
        WHERE symbol=?
        AND timeframe=?
        AND timestamp=?
        """,
        (
            symbol,
            timeframe,
            timestamp
        ))

        result = cursor.fetchone()

        return result[0] > 0



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

        # Duplicate protection
        if self.candle_exists(symbol, timeframe, timestamp):
            return False


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

        return True



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