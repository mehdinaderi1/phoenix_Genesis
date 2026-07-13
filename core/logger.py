from datetime import datetime
from pathlib import Path


class PhoenixLogger:

    def __init__(self, database=None):

        self.database = database

        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)

        self.log_file = self.log_dir / "phoenix.log"

    def write(self, message, level="INFO"):

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        line = f"[{now}] [{level}] {message}"

        print(line)

        with open(self.log_file, "a", encoding="utf-8") as file:
            file.write(line + "\n")

        if self.database:

            try:
                self.database.insert_log(f"[{level}] {message}")

            except Exception as error:
                print(f"Logger Database Error: {error}")

    def info(self, message):
        self.write(message, "INFO")

    def warning(self, message):
        self.write(message, "WARNING")

    def error(self, message):
        self.write(message, "ERROR")

    def success(self, message):
        self.write(message, "SUCCESS")