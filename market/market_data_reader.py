from market.candle import Candle


class MarketDataReader:


    def __init__(self, database):

        self.database = database



    def _row_to_candle(self, row):

        return Candle(
            symbol=row[1],
            timeframe=row[2],
            timestamp=row[3],
            open=row[4],
            high=row[5],
            low=row[6],
            close=row[7],
            volume=row[8]
        )



    def get_all_candles(self, symbol=None):

        cursor = self.database.connection.cursor()


        if symbol:

            cursor.execute("""
            SELECT *
            FROM market_candles
            WHERE symbol = ?
            ORDER BY timestamp ASC
            """,
            (symbol,))

        else:

            cursor.execute("""
            SELECT *
            FROM market_candles
            ORDER BY timestamp ASC
            """)


        rows = cursor.fetchall()


        candles = []

        for row in rows:
            candles.append(
                self._row_to_candle(row)
            )


        return candles



    def get_latest_candle(self, symbol):

        cursor = self.database.connection.cursor()


        cursor.execute("""
        SELECT *
        FROM market_candles
        WHERE symbol = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (symbol,))


        row = cursor.fetchone()


        if row:

            return self._row_to_candle(row)


        return None



    def get_close_prices(self, symbol, timeframe=None):

        cursor = self.database.connection.cursor()

        if timeframe:

            cursor.execute("""
            SELECT *
            FROM market_candles
            WHERE symbol = ?
            AND timeframe = ?
            ORDER BY timestamp ASC
            """,
            (
                symbol,
                timeframe
            ))

        else:

            cursor.execute("""
            SELECT *
            FROM market_candles
            WHERE symbol = ?
            ORDER BY timestamp ASC
            """,
            (symbol,))


        candles = cursor.fetchall()

        prices = []


        for candle in candles:

            prices.append(candle[7])


        return prices