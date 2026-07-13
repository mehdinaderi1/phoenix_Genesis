import sqlite3
import os


class DatabaseManager:

    def __init__(self, db_path="data/phoenix.db"):
        self.db_path = db_path
        self.connection = None


    def connect(self):

        os.makedirs("data", exist_ok=True)

        self.connection = sqlite3.connect(self.db_path)

        self.create_tables()

        print("🗄 Database Connected")


    def create_tables(self):

        cursor = self.connection.cursor()


        cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_logs (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            event TEXT NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
        """)


        cursor.execute("""
        CREATE TABLE IF NOT EXISTS market_candles (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            symbol TEXT NOT NULL,

            timeframe TEXT NOT NULL,

            timestamp INTEGER,

            open REAL,

            high REAL,

            low REAL,

            close REAL,

            volume REAL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
        """)


        self.connection.commit()

        print("✅ Tables Ready")


    def insert_log(self, event):

        cursor = self.connection.cursor()

        cursor.execute(
            "INSERT INTO system_logs(event) VALUES(?)",
            (event,)
        )

        self.connection.commit()


    def insert_candle(self, candle):

        cursor = self.connection.cursor()

        cursor.execute("""
        INSERT INTO market_candles
        (
            symbol,
            timeframe,
            timestamp,
            open,
            high,
            low,
            close,
            volume
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?)

        """,
        (
            candle.symbol,
            candle.timeframe,
            candle.timestamp,
            candle.open,
            candle.high,
            candle.low,
            candle.close,
            candle.volume
        ))

        self.connection.commit()


    def get_candles(self):

        cursor = self.connection.cursor()

        cursor.execute("""
        SELECT * FROM market_candles
        """)

        return cursor.fetchall()
        
    def close(self):

        if self.connection:

            self.connection.close()

            print("🗄 Database Closed")