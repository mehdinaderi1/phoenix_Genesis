from core.database import DatabaseManager
from config.settings import Settings
from core.logger import PhoenixLogger
from core.health import HealthCheck


class PhoenixEngine:

    def __init__(self):
        self.settings = Settings()
        self.database = DatabaseManager()
        self.logger = PhoenixLogger(self.database)
        self.health = HealthCheck(self.logger)

    def start(self):

        print("=" * 45)
        print(f"🦅 {self.settings.APP_NAME}")
        print(f"Version : {self.settings.VERSION}")
        print(f"Exchange: {self.settings.DEFAULT_EXCHANGE}")
        print(f"Demo Mode: {self.settings.DEMO_MODE}")
        print("=" * 45)

        self.database.connect()

        self.logger.write("Phoenix Engine Started Successfully")

        self.database.insert_log("Phoenix Engine Started")
        
        self.health.run()
        self.logger.write("System Health Check Completed")
