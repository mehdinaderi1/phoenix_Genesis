from pathlib import Path


class HealthCheck:
    def __init__(self, logger):
        self.logger = logger

    def run(self):
        folders = [
            "data",
            "logs",
            "backup",
            "reports"
        ]

        self.logger.write("Starting System Health Check...")

        for folder in folders:
            path = Path(folder)

            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
                self.logger.write(f"Created folder: {folder}")
            else:
                self.logger.write(f"OK: {folder}")

        self.logger.write("System Health Check Completed")