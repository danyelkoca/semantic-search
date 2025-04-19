import json
import logging
import os
from logging.handlers import RotatingFileHandler

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Setup environment-based log level
env = os.getenv("ENV", "development")
log_level = logging.INFO if env == "production" else logging.DEBUG


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        return json.dumps(log_obj)


# --- Single App Logger ---
logger = logging.getLogger("semantic-search")
logger.setLevel(log_level)

# Console output (real-time)
console_handler = logging.StreamHandler()
console_handler.setFormatter(JsonFormatter())
logger.addHandler(console_handler)

# Rotating file output (app.log)
file_handler = RotatingFileHandler(
    "logs/app.log", maxBytes=10 * 1024 * 1024, backupCount=5
)
file_handler.setFormatter(JsonFormatter())
logger.addHandler(file_handler)
