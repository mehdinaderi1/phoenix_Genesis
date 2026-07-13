class MarketDataReader:


    def __init__(self, database):

        self.database = database



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


        return cursor.fetchall()



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


        return cursor.fetchone()



    def get_close_prices(self, symbol):

        candles = self.get_all_candles(symbol)

        prices = []


        for candle in candles:

            # Database column:
            # 0 id
            # 1 symbol
            # 2 timeframe
            # 3 timestamp
            # 4 open
            # 5 high
            # 6 low
            # 7 close

            prices.append(candle[7])


        return prices